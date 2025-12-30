import streamlit as st
from pages._base_page import _base_page
from widgets.chart import chart


class charts_page(_base_page):
    def __init__(self, name, db, tango_client):
        super().__init__(name, db)
        
        self.tango_client = tango_client
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
        attr_name = st.text_input("attribute name")
        period_s = st.number_input("period", min_value=0.0)

        if st.button("Add", type="primary"):
            print("dd")


    def _on_delete(self):
        print("on _on_delete")

    def _on_hide(self):
        print("on _on_hide")

    def _on_unhide(self):
        print("on _on_unhide")

    def _on_reorder(self):
        print("on _on_reorder")

    def _on_resize(self):
        print("on _on_resize")
