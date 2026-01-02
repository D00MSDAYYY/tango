import streamlit as st
from pages._base_page import _base_page
from widgets.chart import chart
import tango as tc


class charts_page(_base_page):
    def __init__(self, name, settings, tango_db):
        super().__init__(name, settings)

        self.tango_db = tango_db
        self.charts = dict()

    def __call__(self):
        st.set_page_config(layout="wide")
        st.header("Charts page")

        self._make_toolbar()

        # self.charts.clear()

        # for chart_doc in self.db.table("charts").all():
        #     chart_name = chart_doc.name
        #     self.charts[chart_name] = chart(self.db, chart_name)

    def _make_toolbar(self):
        """Функциональный тулбар с реальными кнопками Streamlit"""

        toolbuttons = [
            ("Add", 2, self._on_add),
            ("Delete", 2, self._on_delete),
            ("Hide", 1, self._on_hide),
            ("Unhide", 1, self._on_unhide),
            ("Reorder", 1, self._on_reorder),
            ("Resize", 1, self._on_resize),
        ]
        columns = st.columns([size for (name, size, func) in toolbuttons])

        for column, toolbutton in zip(columns, toolbuttons):
            with column:
                name, size, func = toolbutton
                with st.popover(name, width="stretch"):
                    func()

    def _on_add(self):
        tango_db = self.tango_db

        device_names = tango_db.get_device_exported("*")
        device_name = st.selectbox("Select device", device_names)
        proxy = tc.DeviceProxy(
            "tango://" + tango_db.host_str + ":" + tango_db.port_str + "/" + device_name
        )

        attribute_names = [
            attribute.name
            for attribute in proxy.get_attribute_config_ex([tc.constants.AllAttr])
        ]
        attribute_name = st.selectbox("Select attribute", attribute_names)

        if st.button("Add", type="primary"):
            pass

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
