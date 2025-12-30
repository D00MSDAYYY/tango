import streamlit as st
import tinydb as tdb
from types import SimpleNamespace
from abc import ABC, abstractmethod


class _base_chart(ABC):
    def __init__(self, db, name):
        self.db = db
        self.name = name

        doc_list = db.table("charts").search(tdb.where("name") == self.name)
        self.settings = SimpleNamespace(doc_list[0] if doc_list else dict())

    @abstractmethod
    def __call__(self):
        pass
