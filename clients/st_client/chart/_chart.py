import streamlit as st
from abc import ABC, abstractmethod
from typing import final


class _chart(ABC):
    def __init__(self, name, db):
        self.db = db
        self.name = name

    @final
    def show(self, *args, **kwds):
        with st.container(border=True):
            
            st.write("chart ", self.name)
            self.content(*args, **kwds)

    @abstractmethod
    def content(self, *args, **kwds):
        pass
