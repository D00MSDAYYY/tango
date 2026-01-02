import streamlit as st
from pages._base_page import _base_page


class system_page(_base_page):
    def __init__(self, name, settings):
        super().__init__(name, settings)

    def __call__(self):
        st.set_page_config(layout="wide", page_title="system_page")
        st.header("System page")
