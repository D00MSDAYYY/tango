import streamlit as st
from pgs._base_page import _base_page
from widgets.chart import chart
import chart_builder as cb


class charts_page(_base_page):
    def __init__(self, name, settings, tango_db):
        super().__init__(name, settings)
        self.tango_db = tango_db
        self.charts = self.settings.setdefault("charts", [])
        print("!1!", type(self.charts))

    def __call__(self):
        st.set_page_config(layout="wide")
        st.header(body="Charts page")

        self._make_toolbar()

        # self.charts.clear()

        # for chart_doc in self.db.table("charts").all():
        #     chart_name = chart_doc.name
        #     self.charts[chart_name] = chart(self.db, chart_name)

    def _make_toolbar(self):

        toolbuttons = [
            ("Add", 2, self._on_add),
            ("Delete", 2, self._on_delete),
            ("Hide", 1, self._on_hide),
            ("Unhide", 1, self._on_unhide),
            ("Reorder", 1, self._on_reorder),
            ("Resize", 1, self._on_resize),
        ]
        columns = st.columns(spec=[size for (name, size, func) in toolbuttons])

        for column, toolbutton in zip(columns, toolbuttons):
            with column:
                name, size, func = toolbutton
                with st.popover(label=name, width="stretch"):
                    func()

    def _on_add(self):
        builder = cb.tango_builder(
            existing_charts=self.settings["charts"], tango_db=self.tango_db
        )
        new_settings = builder.get_new_chart_settings()
        if new_settings:
            self.charts.append(new_settings)
            print("!2!", type(self.charts))

            new_chart = builder.build_chart_from_settings(new_settings)

    def _on_delete(self):
        pass

    def _on_hide(self):
        pass

    def _on_unhide(self):
        pass

    def _on_reorder(self):
        pass

    def _on_resize(self):
        pass
