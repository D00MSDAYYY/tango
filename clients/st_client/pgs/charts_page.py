import streamlit as st
from pgs._base_page import _base_page
from chart.chart import chart
import chart_builder.tango_chart_builder as cb


class charts_page(_base_page):
    def __init__(self, name, settings, tango_db):
        super().__init__(name, settings)
        self.tango_db = tango_db
        self.settings = settings

        self.tango_charts_builder = cb.tango_builder(
            existing_charts=self.settings["charts"], tango_db=self.tango_db
        )
        self.charts = []
        self.toolbar = None

    def show(self, *args, **kwds):
        st.set_page_config(layout="wide")
        st.header(body="Charts page")

        self._make_toolbar()
        if self.toolbar:
            self.toolbar.show()
        self._make_grid()

    def _make_toolbar(self):
        from toolbar.toolbar import toolbar
        from widgets.button import button
        from widgets.popover import popover

        toolbuttons = [
            popover(label="Add", width="stretch",fraction=2, on_click=self._on_add),
            popover(label="Delete", width="stretch", fraction=2,on_click=self._on_delete),
            button(label="Hide", width="stretch", fraction=1,on_click=self._on_hide),
            button(label="Unhide", width="stretch", fraction=1,on_click=self._on_unhide),
            button(label="Reorder", width="stretch", fraction=1,on_click=self._on_reorder),
            button(label="Resize", width="stretch",fraction=1, on_click=self._on_resize),
        ]
        self.toolbar = toolbar(toolbuttons)

    def _on_add(self):
        tango_builder = self.tango_charts_builder
        new_settings = tango_builder.get_new_chart_settings()

        if new_settings:
            self.settings["charts"].append(new_settings)
            new_chart = (
                tango_builder.build_chart_from_settings(new_settings) or None
            )  # TODO return dummy chart overwise

            if new_chart:
                self.charts.append(new_chart)

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

    def _make_grid(self):
        for chart in [
            self.tango_charts_builder.build_chart_from_settings(s)
            for s in self.settings["charts"]
        ]:
            if chart:
                chart.show()
        # self.charts.clear()

        # for chart_doc in self.db.table("charts").all():
        #     chart_name = chart_doc.name
        #     self.charts[chart_name] = chart(self.db, chart_name)
