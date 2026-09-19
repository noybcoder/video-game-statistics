import streamlit as st
from page_utils import set_up_page
from api_client import fetch_or_halt

set_up_page('Developer Insights', '🛠️', """This page shows the industry overview""")

genre_data = fetch_or_halt('analytics/genres_per_developer')
    
genre_data = genre_data.rename(columns={
    'developer': 'Developer', 'genre': 'Genre', 
    'total_game_count': 'Number of Games Developed', 'pct_of_total_game_count': 'Percentage of Games Developed'
})

col1, col2 = st.columns(2)

with col1:
    developer = st.selectbox(
        'Filter by developer',
        options=genre_data['Developer'].unique(),
        index=None,
        placeholder='Type to find developer...'
    )

with col2:
    genres = st.multiselect(
        'Filter by genres:',
        options=genre_data['Genre'].unique(),
        default=None,
        placeholder='Type to find genres...'
    )

filtered_data = genre_data.copy()

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
