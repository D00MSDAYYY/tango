import streamlit as st
from types import SimpleNamespace
import settings as stgs

class observer_app:
    def __init__(self):
        pass

    def run(self):
        if self._connect_to_db() and self._connect_to_tango_db() and self._make_pages():
            pages = self.pages
            nav = st.navigation(
                pages={
                    "Work": [
                        pages.charts_page,
                        pages.logs_page,
                        pages.watchdogs_page,
                    ],
                    "Settings": [pages.system_page],
                }
            )
            nav.run()

    def _connect_to_db(self):
        if hasattr(self, "settings"):
            return True

        file_path = st.text_input(
            label="Enter database's file path",
            value="./my_db.json",  # TODO mb change to placeholder= in future
        )

        if st.button(label="Connect", type="primary"):
            try:
                self.settings = stgs.settings_singletone.from_file(file_path=file_path)
                st.rerun()
            except Exception as e:
                st.warning(body=f"Can't open {file_path}")
                st.stop()

    def _connect_to_tango_db(self):
        if hasattr(self, "tango_db"):
            return True

        tango_settings = self.settings.setdefault("tango_settings", {})
        tango_hosts = tango_settings.setdefault("tango_hosts", [])

        TANGO_HOST = st.selectbox(
            label="Enter TANGO_HOST",
            options=[f"{elem["host"]}:{elem["port"]}" for elem in tango_hosts],
            placeholder="127.0.0.1:11000",
            accept_new_options=True,
        )

        if st.button(label="Connect", type="primary"):
            host, port = TANGO_HOST.split(":")
            try:
                import tango as tc

                tango_db = tc.Database(host, port)
                self.tango_db = tango_db

                for h in tango_hosts:
                    h["last_used"] = False

                if not any(
                    h["host"] == host and h["port"] == port for h in tango_hosts
                ):
                    tango_hosts.append({"host": host, "port": port})

                for h in tango_hosts:
                    if h["host"] == host and h["port"] == port:
                        h["last_used"] = True
                        break

                tango_db.settings = tango_settings
                tango_db.host = host
                tango_db.port = port

                st.rerun()

            except Exception as e:
                st.warning(body=f"Error:{e}")
                st.stop()

    def _make_pages(self):
        if hasattr(self, "pages"):
            return True

        def _make_page(page_callable):
            return st.Page(
                page=page_callable,
                title=page_callable.name,
                url_path=page_callable.name,
            )

        from pgs import charts_page, logs_page, system_page, watchdogs_page

        self.settings
        self.pages = SimpleNamespace(
            charts_page=_make_page(
                charts_page.charts_page(
                    "charts",
                    self.settings.setdefault("charts_page_settings", {}),
                    self.tango_db,
                )
            ),
            logs_page=_make_page(
                logs_page.logs_page(
                    "logs", self.settings.setdefault("logs_page_settings", {})
                )
            ),
            system_page=_make_page(
                system_page.system_page(
                    "system", self.settings.setdefault("system_page_settings", {})
                )
            ),
            watchdogs_page=_make_page(
                watchdogs_page.watchdogs_page(
                    "watchdogs", self.settings.setdefault("watchdogs_page_settings", {})
                )
            ),
        )

        st.rerun()
