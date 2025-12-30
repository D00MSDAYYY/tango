import streamlit as st
import tinydb as tdb
from types import SimpleNamespace
import os


class observer_app:
    def __init__(self):
        pass

    def __call__(self):

        self._connect_to_db()
        self._connect_to_tango()
        self._make_pages()

        if hasattr(self, "pages"):
            pages = self.pages
            nav = st.navigation(
                {
                    "Work": [pages.charts_page, pages.logs_page, pages.watchdogs_page],
                    "Settings": [pages.system_page],
                }
            )
            nav.run()

    def _connect_to_db(self):
        if hasattr(self, "db"):
            return

        db_name = st.text_input("Enter database's name", "my_db.json")

        if st.button("Connect", type="primary"):
            self.db = tdb.TinyDB(db_name)
            st.rerun()

    def _make_pages(self):
        if (
            hasattr(self, "pages")
            or not hasattr(self, "db")
            or not hasattr(self, "tango_client")
        ):
            return

        def _make_page(page_callable):
            return st.Page(
                page_callable, title=page_callable.name, url_path=page_callable.name
            )

        from pages import charts_page, logs_page, system_page, watchdogs_page

        pages = dict(
            charts_page=_make_page(charts_page.charts_page("charts", self.db, 1)),
            logs_page=_make_page(logs_page.logs_page("logs", self.db)),
            system_page=_make_page(system_page.system_page("system", self.db)),
            watchdogs_page=_make_page(
                watchdogs_page.watchdogs_page("watchdogs", self.db)
            ),
        )

        self.pages = SimpleNamespace(**pages)

    def _connect_to_tango(self):
        if hasattr(self, "tango_client") or not hasattr(self, "db"):
            return

        st.text_input("Enter tango host", os.environ.get("TANGO_HOST") or "")

        if st.button("push me", type="primary"):
            self.tango_client = 1
            st.rerun()
