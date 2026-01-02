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
        if hasattr(self, "db"):
            return True

        file_path = st.text_input("Enter database's file path", "./my_db.json")

        if st.button("Connect", type="primary"):
            try:
                self.settings = stgs.settings(file_path=file_path)
                st.rerun()
            except Exception as e:
                st.warning(f"Can't open {file_path}")
                st.stop()

    def _make_pages(self):
        if hasattr(self, "pages"):
            return True

        def _make_page(page_callable):
            return st.Page(
                page_callable, title=page_callable.name, url_path=page_callable.name
            )

        from pages import charts_page, logs_page, system_page, watchdogs_page

        settings = self.settings
        pages = dict(
            charts_page=_make_page(
                charts_page.charts_page(
                    "charts",
                    settings.extract_or_create_settings("charts"),
                    self.tango_db,
                )
            ),
            logs_page=_make_page(logs_page.logs_page("logs", self.db)),
            system_page=_make_page(system_page.system_page("system", self.db)),
            watchdogs_page=_make_page(
                watchdogs_page.watchdogs_page("watchdogs", self.db)
            ),
        )

        self.pages = SimpleNamespace(**pages)
        st.rerun()

    def _connect_to_tango_db(self):
        if hasattr(self, "tango_db"):
            return True

        tango_settings = self.db.get("tango_settings", dict())  #
        self.db["tango_settings"] = tango_settings
        # TODO creae aux func for this construction

        TANGO_HOST = st.text_input(
            "Enter TANGO_HOST", tango_settings.get("TANGO_HOST", "host:port")
        )
        is_save = st.checkbox("Save in db")

        if st.button("Connect", type="primary"):
            host, port = TANGO_HOST.split(":")
            try:
                import tango as tc

                tango_db = tc.Database(host, port)
                tango_db.host_str = host
                tango_db.port_str = port
                self.tango_db = tango_db

                if is_save:
                    tango_settings["TANGO_HOST"] = TANGO_HOST
                    self._save_db()

                st.rerun()

            except Exception as e:
                st.warning(f"Can't connect to {TANGO_HOST}")
                st.stop()

    def _save_db(self):
        try:
            with open(self.db_file_name, "w") as f:
                json.dump(self.db, f)
        except Exception as e:
            st.error(f"Ошибка сохранения: {e}")
