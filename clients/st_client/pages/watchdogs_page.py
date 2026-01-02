import streamlit as st
from pages._base_page import _base_page


class watchdogs_page(_base_page):
    def __init__(self, name, settings):
        super().__init__(name, settings)
        print("2\n\n\n\n\n\n", settings, type(settings))

    def __call__(self):
        st.set_page_config(layout="wide", page_title="watchdogs_page")
        st.header("Watchdogs page")
