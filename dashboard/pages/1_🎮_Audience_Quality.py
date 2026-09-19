import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
from api_client import fetch_or_halt

st.set_page_config(page_title='Audience & Quality', page_icon='🎮')

st.markdown('# Audience & Quality')
st.sidebar.header('Audience & Quality')
st.write(
    """This page shows the industry overview"""
)

data = fetch_or_halt('analytics/most_popular_genres_by_year')

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