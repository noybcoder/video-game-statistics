import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

HOST = 'http://127.0.0.1:8000'

@st.cache_data(ttl=3600)
def get_data(endpoint: str) -> pd.DataFrame:
    url = f'{HOST}/{endpoint}'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f'Failed to load data from {url}: {e}')
        return pd.DataFrame()


def fetch_or_halt(endpoint: str) -> pd.DataFrame:
    data = get_data(endpoint)

    if data.empty:
        st.warning('No data available.')
        st.stop()
    return data