import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
from page_utils import set_up_page
from api_client import fetch_or_halt

set_up_page('Video Game Industry Analytics', '📊', """This page shows the industry overview""")

data = fetch_or_halt('analytics/genre_distribution')

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