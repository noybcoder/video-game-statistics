import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title='Developer Insights', page_icon='🛠️')

st.markdown('# Developer Insights')
st.sidebar.header('Developer Insights')
st.write(
    """This page shows the industry overview"""
)

HOST = 'http://127.0.0.1:8000'
URL = f'{HOST}/analytics/genres_per_developer'

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
data.rename(inplace=True, columns={
    'developer': 'Developer', 'genre': 'Genre', 
    'total_game_count': 'Number of Games Developed', 'pct_of_total_game_count': 'Percentage of Games Developed'})

st.dataframe(data, use_container_width=True, hide_index=True)
