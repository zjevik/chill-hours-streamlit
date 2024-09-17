import streamlit as st
import pandas as pd
import math
from pathlib import Path
import pgeocode
import plotly.express as px
import plotly.figure_factory as ff
import requests
import datetime
import ast

def zip_to_gps(zipcode):
    nomi = pgeocode.Nominatim('us')
    location = nomi.query_postal_code(zipcode)
    return float(location.latitude), float(location.longitude)

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Chill hours',
    page_icon=':snowflake:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_data(lat,lon,from_year,to_year):
    start_date = f'{from_year}-07-01'
    end_date = f'{to_year}-06-01'
    if datetime.datetime.strptime(end_date, "%Y-%m-%d") > datetime.datetime.now():
        # use yesterday's date
        end_date = datetime.datetime.now().date() - datetime.timedelta(days=1)
    url = f'https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m&temperature_unit=fahrenheit'
    response = requests.get(url).json()
    df = pd.DataFrame(response['hourly'])
    df['time'] = pd.to_datetime(df['time'])
    df['year'] = (df['time'] + pd.DateOffset(months=6)).dt.year
    return df, (response['latitude'], response['longitude'])

# -----------------------------------------------------------------------------
# Draw the actual page


# Add some spacing
''
''

time_now = datetime.datetime.now()

max_value = time_now.year+1

col1, col2 = st.columns([0.2,0.8], gap='medium')
with col1:
    zip_code = st.text_input('zip code', help='5 digit zip code', type="default")

with col2:
    from_year, to_year = st.slider(
        'Which years are you interested in?',
        min_value=1980,
        max_value=max_value,
        value=[2020, max_value])

if (len(zip_code) != 5) or (not zip_code.isdecimal()):
    st.error('Missing 5 digit zip code!')

else:
    lat, lon = zip_to_gps(zip_code)

    ''
    ''
    chill_min, chill_max = st.slider(
        'Chill temperature range [fahrenheit]',
        min_value=-60,
        max_value=45,
        value=[32, 45])


    df, weather_gps = get_data(lat,lon,from_year,to_year)
    df['count'] = (df['temperature_2m'] <= chill_max) & (df['temperature_2m'] >= chill_min)
    df['chill_hours'] = df.groupby('year')['count'].cumsum()
    df['day_cnt'] = df.groupby('year').cumcount()
    df['date'] = df['time'].dt.strftime('%B-%d')
    df['max_chill_hours'] = df['year'].map(df.groupby('year')['chill_hours'].max().to_dict())

    # drop zero values
    df = df[df['chill_hours']>0]

    # drop max values
    df = df[df['chill_hours'] != df['max_chill_hours']]
    ''
    st.header('Chill hours', divider='gray')
    fig = px.line(df, x='date', y='chill_hours', color='year', category_orders={'date':df.sort_values('day_cnt')['date']})
    st.plotly_chart(fig)


''

st.text("""This app uses weather data from https://open-meteo.com/""") 