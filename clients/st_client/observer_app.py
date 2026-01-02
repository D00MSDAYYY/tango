import streamlit as st
from types import SimpleNamespace
import settings as stgs


class observer_app:
    def __init__(self):
        pass

    def __call__(self):
        if self._connect_to_db() and self._connect_to_tango_db() and self._make_pages():
            pages = self.pages
            nav = st.navigation(
                {
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

        file_path = st.text_input("Enter database's file path", "./my_db.json")

        if st.button("Connect", type="primary"):
            try:
                self.settings = stgs.settings.from_file(file_path=file_path)
                st.rerun()
            except Exception as e:
                st.warning(f"Can't open {file_path}")
                st.stop()

    def _connect_to_tango_db(self):
        if hasattr(self, "tango_db"):
            return True

        tango_settings = stgs.settings.from_settings(self.settings, "tango_settings")
        tango_hosts = tango_settings.get_or_create("tango_hosts", [])

        TANGO_HOST = st.selectbox(
            "Enter TANGO_HOST",
            [f"{elem["host"]}:{elem["port"]}" for elem in tango_hosts],
            placeholder="127.0.0.1:11000",
            accept_new_options=True,
        )

        if st.button("Connect", type="primary"):
            host, port = TANGO_HOST.split(":")
            try:
                import tango as tc

                tango_db = tc.Database(host, port)
                self.tango_db = tango_db

                is_duplicate = False
                for h in tango_hosts:
                    if h["host"] == host and h["port"] == port:
                        h["last_used"] = True
                        is_duplicate = True
                    else:
                        h["last_used"] = False
                if not is_duplicate:
                    tango_hosts.append({"host": host, "port": port, "last_used": True})

                tango_db.settings = tango_settings
                tango_db.host = host
                tango_db.port = port

                st.rerun()

            except Exception as e:
                st.warning(f"Can't connect to {TANGO_HOST}")
                st.stop()

    def _make_pages(self):
        if hasattr(self, "pages"):
            return True

        def _make_page(page_callable):
            return st.Page(
                page_callable, title=page_callable.name, url_path=page_callable.name
            )

        from pages import charts_page, logs_page, system_page, watchdogs_page

        from_settings = stgs.settings.from_settings
        self_settings = self.settings
        pages = dict(
            charts_page=_make_page(
                charts_page.charts_page(
                    "charts",
                    from_settings(self_settings, "charts_page_settings"),
                    self.tango_db,
                )
            ),
            logs_page=_make_page(
                logs_page.logs_page(
                    "logs", from_settings(self_settings, "logs_page_settings")
                )
            ),
            system_page=_make_page(
                system_page.system_page(
                    "system", from_settings(self_settings, "system_page_settings")
                )
            ),
            watchdogs_page=_make_page(
                watchdogs_page.watchdogs_page(
                    "watchdogs", from_settings(self_settings, "watchdogs_page_settings")
                )
            ),
        )

        self.pages = SimpleNamespace(**pages)
        st.rerun()
