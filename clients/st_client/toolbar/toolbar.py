from abc import ABC, abstractmethod
import streamlit as st
from widgets.button import button
from typing import Protocol, Sequence


class Showable(Protocol):
    def show(self): ...


class toolbar:
    def __init__(self, widgets):
        self.toolbuttons: list[Showable] = widgets

    @abstractmethod
    def show(self):
        columns = st.columns(spec=[btn.fraction for btn in self.toolbuttons])

        for column, toolbutton in zip(columns, self.toolbuttons):
            with column:
                toolbutton.show()
