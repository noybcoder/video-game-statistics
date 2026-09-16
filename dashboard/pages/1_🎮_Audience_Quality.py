import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title='Audience & Quality', page_icon='🎮')

st.markdown('# Audience & Quality')
st.sidebar.header('Audience & Quality')
st.write(
    """This page shows the industry overview"""
)

HOST = 'http://127.0.0.1:8000'
URL = f'{HOST}/analytics/most_popular_genres_by_year'

@st.cache_data(ttl=3600)
def get_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()
    
data = get_data(URL)
heatmap_data = data.pivot(
    index="genre",
    columns="release_year",
    values="weighted_average_rating"
)

fig = px.imshow(
    heatmap_data,
    labels=dict(x="Year", y="Genre", color="Weighted Average Rating"),
    title="Genre by Year",
    color_continuous_scale="RdYlGn",
    aspect="auto",
    text_auto=True
)

fig.update_yaxes(
    tickmode='array',
    tickvals=list(range(len(heatmap_data.index))),
    ticktext=list(heatmap_data.index)
)

st.plotly_chart(fig, use_container_width=True)