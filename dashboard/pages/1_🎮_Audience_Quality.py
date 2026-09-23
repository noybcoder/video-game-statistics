import streamlit as st
from page_utils import set_up_page, generate_heat_map, display_heat_map
from api_client import fetch_or_halt

set_up_page(
    'Audience & Quality', 
    '🎮', 
    "Tracks how top-rated genres have shifted over the past 15 years, based on weighted audience ratings."
)

data = fetch_or_halt('analytics/most_popular_genres_by_year')

fig = generate_heat_map(
    data=data, index='genre', columns='release_year', values='weighted_average_rating',
    x_label='Year', y_label='Genre', color_label='Weighted Average Rating', color_scale='RdYlGn'
)

display_heat_map('Genre Ratings by Year', fig)