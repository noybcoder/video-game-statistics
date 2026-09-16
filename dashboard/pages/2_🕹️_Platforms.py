import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title='Platforms', page_icon='🕹️')

st.markdown('# Platforms')
st.sidebar.header('Platforms')
st.write(
    """This page shows the industry overview"""
)

HOST = 'http://127.0.0.1:8000'
URL = f'{HOST}/analytics/most_popular_platforms_by_year'

@st.cache_data(ttl=3600)
def get_data(url):
    response = requests.get(url)
    return pd.DataFrame(response.json())

data = get_data(URL)
heatmap_data = data.pivot(
    index="platform",
    columns="release_year",
    values="game_count"
)

fig = px.imshow(
    heatmap_data,
    labels=dict(x="Year", y="Platform", color="Number of Games"),
    title="Platform by Year",
    color_continuous_scale="RdYlGn",   # Red = low, Green = high
    aspect="auto",
    text_auto=True                      # Show values inside cells
)

st.plotly_chart(fig, use_container_width=True)
