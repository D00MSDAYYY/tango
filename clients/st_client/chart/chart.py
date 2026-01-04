import streamlit as st
from chart._chart import _chart 

class chart(_chart):
    def __init__(self, db, name):
        super().__init__(db, name)

    def content(self, *args, **kwds):
        st.write("this is derived class content")


