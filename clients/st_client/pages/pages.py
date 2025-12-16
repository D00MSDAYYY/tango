import streamlit as st
from pathlib import Path

def _make_page_from_module(module):
    path = Path(module.__file__)
    title = path.stem.replace("_page", "").strip()
    return st.Page(page=path, title=title)

from  .charts_page import charts_page

charts_page = _make_page_from_module(charts_page)