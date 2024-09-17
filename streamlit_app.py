import streamlit as st
import pandas as pd
import math
from pathlib import Path
import pgeocode
import plotly.express as px
import requests
import datetime
import ast

def zip_to_gps(zipcode):
    nomi = pgeocode.Nominatim('us')
    location = nomi.query_postal_code(zipcode)
    return float(location.latitude), float(location.longitude)

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
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

min_value = 2020
max_value = time_now.year

col1, col2 = st.columns([0.2,0.8], gap='medium')
with col1:
    zip_code = st.text_input('zip code', help='5 digit zip code', type="default")

with col2:
    from_year, to_year = st.slider(
        'Which years are you interested in?',
        min_value=min_value,
        max_value=max_value,
        value=[min_value, max_value])


lat, lon = zip_to_gps(zip_code)

''
''
chill_min, chill_max = st.slider(
    'Chill temperature range [fahrenheit]',
    min_value=-60,
    max_value=45,
    value=[-60, 45])


df, weather_gps = get_data(lat,lon,from_year,to_year)
print(df.shape)
print(df.head())

''
''
''

# fig = px.

# # Filter the data
# filtered_gdp_df = gdp_df[
#     (gdp_df['Country Code'].isin(selected_countries))
#     & (gdp_df['Year'] <= to_year)
#     & (from_year <= gdp_df['Year'])
# ]

# st.header('GDP over time', divider='gray')

''

# st.line_chart(
#     filtered_gdp_df,
#     x='Year',
#     y='GDP',
#     color='Country Code',
# )

''
''


# first_year = gdp_df[gdp_df['Year'] == from_year]
# last_year = gdp_df[gdp_df['Year'] == to_year]

# st.header(f'GDP in {to_year}', divider='gray')

# ''

# cols = st.columns(4)

# for i, country in enumerate(selected_countries):
#     col = cols[i % len(cols)]

#     with col:
#         first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
#         last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

#         if math.isnan(first_gdp):
#             growth = 'n/a'
#             delta_color = 'off'
#         else:
#             growth = f'{last_gdp / first_gdp:,.2f}x'
#             delta_color = 'normal'

#         st.metric(
#             label=f'{country} GDP',
#             value=f'{last_gdp:,.0f}B',
#             delta=growth,
#             delta_color=delta_color
#         )
