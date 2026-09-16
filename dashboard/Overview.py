import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="Overview", page_icon="📊")

st.title('Video Game Industry Analytics')
st.sidebar.header("Video Game Industry Analytics")

st.write(
    """This page shows the industry overview"""
)

HOST = 'http://127.0.0.1:8000'
URL = f'{HOST}/analytics/genre_distribution'

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
st.table(data)
