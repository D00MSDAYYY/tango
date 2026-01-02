import streamlit as st
from pages._base_page import _base_page


class logs_page(_base_page):
    def __init__(self, name, settings):
        super().__init__(name, settings)

    def __call__(self):
        st.set_page_config(layout="wide", page_title="logs_page")
        st.header("Logs page")
