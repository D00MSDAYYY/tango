from chart.chart import chart as chart
import streamlit as st
import tango as tc
from chart_builder._chart_builder import _chart_builder as _chart_builder


class tango_builder(_chart_builder):
    def __init__(self, existing_charts, tango_db):
        super().__init__()
        self.existing_charts = existing_charts
        self.tango_db = tango_db

    def get_new_chart_settings(self):

        chart_name = st.text_input(label="Enter new chart name")
        if any(chart_name == c["name"] for c in self.existing_charts):
            st.error(
                body=f"Chart with name '{chart_name}' already exists, choose another name"
            )
            chart_name = ""
        if chart_name:
            tango_db = self.tango_db

            device_names = tango_db.get_device_exported("*")
            device_name = st.selectbox(
                label="Select device",
                options=device_names,
                index=None,
                accept_new_options=False,
            )
            if device_name:
                proxy = tc.DeviceProxy(
                    "tango://" + tango_db.host + ":" + tango_db.port + "/" + device_name
                )
                device_info = proxy.info()
                with st.expander(label="Device info"):
                    st.write(device_info)

                attributes = proxy.get_attribute_config_ex([tc.constants.AllAttr])

                attribute_names = [attribute.name for attribute in attributes]
                attribute_name = st.selectbox(
                    label="Select attribute",
                    options=attribute_names,
                    index=None,
                    accept_new_options=False,
                )
                if attribute_name:
                    attr_config = proxy.get_attribute_config(attribute_name)
                    with st.expander(label="Attribute info"):
                        st.write(attr_config)

                    event_types = {
                        "change event": tc.EventType.CHANGE_EVENT,
                        "periodic event": tc.EventType.PERIODIC_EVENT,
                        "archive event": tc.EventType.ARCHIVE_EVENT,
                    }
                    event_type_str = st.selectbox(
                        label="Select event type",
                        options=event_types.keys(),
                        index=None,
                        accept_new_options=False,
                    )
                    if event_type_str:
                        event_type = event_types[event_type_str]

                        new_polling_period = st.number_input(
                            label="Enter polling period (ms)", min_value=0, value=1000
                        )
                        if new_polling_period:
                            if st.button("Add", type="primary"):
                                try:
                                    old_polling_period = (
                                        proxy.get_attribute_poll_period(attribute_name)
                                    )
                                    proxy.poll_attribute(
                                        attribute_name,
                                        (
                                            new_polling_period
                                            if new_polling_period < old_polling_period
                                            or old_polling_period <= 0
                                            else old_polling_period
                                        ),
                                    )
                                    event_id = proxy.subscribe_event(
                                        attribute_name,
                                        event_type,
                                        lambda event_data: print(event_data),
                                        stateless=False,
                                    )
                                    new_chart_settings = dict(
                                        name=chart_name,
                                        device_name=device_name,
                                        attribute_name=attribute_name,
                                        event_type_str=event_type_str,
                                        new_polling_period=new_polling_period,
                                    )
                                    st.success(
                                        f"✅ Subscribed to {event_type_str} event (ID: {event_id})"
                                    )
                                    return new_chart_settings

                                except Exception as e:
                                    st.warning(f"Error: {e}")

    def build_chart_from_settings(self, chart_settings) -> chart.chart | None:
        bc = chart(chart_settings["name"], None)
        return bc
