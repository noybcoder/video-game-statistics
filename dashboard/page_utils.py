import streamlit as st
import plotly.express as px

def set_up_page(title: str, icon: str, description: str) -> None:
    st.set_page_config(page_title=title, page_icon=icon, layout='wide')
    st.markdown(f'# {title}')
    st.sidebar.header(title)
    st.write(description)

def fix_heatmap_yaxis_labels(fig, y_labels):
    fig.update_yaxes(
        tickmode='array',
        tickvals=list(range(len(y_labels))),
        ticktext=list(y_labels)
    )
    return fig

def generate_heat_map(data, index, columns, values, x_label, y_label, color_label, color_scale, min_height=500, row_height=20):
    heatmap_data = data.pivot(index=index, columns=columns, values=values)

    fig = px.imshow(
        heatmap_data,
        labels=dict(x=x_label, y=y_label, color=color_label),
        color_continuous_scale=color_scale,
        aspect="auto",
        text_auto=True
    )

    fig.update_layout(height=max(min_height, len(heatmap_data.index) * row_height))
    return fix_heatmap_yaxis_labels(fig, heatmap_data.index)

def display_heat_map(subheader, fig):
    st.subheader(subheader)
    st.plotly_chart(fig, use_container_width=True)