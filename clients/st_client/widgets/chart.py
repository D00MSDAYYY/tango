import streamlit as st
from widgets._base_chart import _base_chart

class chart(_base_chart):
    def __init__(self, db, name):
        super().__init__(db, name)

    def __call__(self):
        pass


