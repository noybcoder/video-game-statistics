import streamlit as st
from page_utils import set_up_page, generate_heat_map, display_heat_map
from api_client import fetch_or_halt

set_up_page(
    'Platforms', 
    '🕹️', 
    "Shows release volume trends across the industry's most active platforms over time."
)

data = fetch_or_halt('analytics/most_popular_platforms_by_year')

fig = generate_heat_map(
    data=data, index='platform', columns='release_year', values='game_count',
    x_label='Year', y_label='Platform', color_label='Number of Games', color_scale='Viridis'
)

display_heat_map('Platform Release Volume by Year', fig)