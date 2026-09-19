import streamlit as st
import pandas as pd
import requests

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
if data.empty:
    st.warning("No data available.")
    st.stop()
    
data = data.rename(columns={
    'developer': 'Developer', 'genre': 'Genre', 
    'total_game_count': 'Number of Games Developed', 'pct_of_total_game_count': 'Percentage of Games Developed'
})

col1, col2 = st.columns(2)

with col1:
    developer = st.selectbox(
        'Filter by developer',
        options=data['Developer'].unique(),
        index=None,
        placeholder='Type to find developer...'
    )

with col2:
    genres = st.multiselect(
        'Filter by genres:',
        options=data['Genre'].unique(),
        default=None,
        placeholder='Type to find genres...'
    )

filtered_data = data.copy()

if developer:
    filtered_data = filtered_data[filtered_data['Developer'] == developer]
if genres:
    filtered_data = filtered_data[filtered_data['Genre'].isin(genres)]

filtered_data = filtered_data.sort_values(by=['Percentage of Games Developed', 'Genre'], ascending=[False, True])

st.subheader('Genre Specialization Among Active Developers')
st.dataframe(filtered_data, use_container_width=True, hide_index=True, column_config={
        "Percentage of Games Developed": st.column_config.ProgressColumn(
            "Percentage of Games Developed",
            format="%.1f%%",
            min_value=0,
            max_value=100,
        )
    })
st.caption("Developers with multiple genres listed are tied for their top genre specialization.")
