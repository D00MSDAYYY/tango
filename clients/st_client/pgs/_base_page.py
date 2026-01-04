from abc import ABC, abstractmethod
import streamlit as st
from typing import Any, final

class _base_page(ABC):
    def __init__(self, name, settings):
        self.settings = settings
        self.name = name

    @final 
    def __call__(self, *args, **kwds):
        self.show(*args, **kwds)
    
    @abstractmethod
    def show(self, *args, **kwds):
        pass
