import streamlit as st

def set_up_page(title: str, icon: str, description: str) -> None:
    st.set_page_config(page_title=title, page_icon=icon)
    st.markdown(f'# {title}')
    st.sidebar.header(title)
    st.write(description)