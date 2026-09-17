import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

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

grouped_data = data \
    .groupby(by='genre') \
    .agg(total_game_count=('game_count', 'sum')) \
    .reset_index() \
    .sort_values(by='total_game_count', ascending=False)

grouped_data['cumulative_pct'] = grouped_data['total_game_count'].cumsum() / grouped_data['total_game_count'].sum()
grouped_data['new_genre'] = np.where(grouped_data['cumulative_pct'] > 0.8, 'Others', grouped_data['genre'])

print(grouped_data)

fig = px.pie(names=grouped_data['new_genre'], values=grouped_data['total_game_count'])
fig.update_traces(textposition='inside', textinfo='label+percent')
fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False)


st.plotly_chart(fig)