import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tango import DeviceProxy
import time


class TangoPollingMonitor:
    def __init__(self, device_name):
        self.device_name = device_name
        self.device = None
        self.polling_interval = 1.0  # секунды
        self.last_poll_time = {}
        self.subscribed_attrs = set()

    def connect(self):
        try:
            self.device = DeviceProxy(self.device_name)
            self.device.ping()
            return True
        except Exception as e:
            st.error(f"Ошибка подключения: {e}")
            return False

    def subscribe_to_attribute(self, attr_name):
        """Добавляем атрибут в список для опроса"""
        if attr_name in self.get_available_attributes():
            self.subscribed_attrs.add(attr_name)
            self.last_poll_time[attr_name] = 0
            return True
        return False

    def poll_attributes(self):
        """Опрос текущих значений атрибутов"""
        data = {}
        current_time = time.time()

        for attr_name in self.subscribed_attrs:
            # Проверяем, нужно ли опрашивать (по интервалу)
            if current_time - self.last_poll_time.get(attr_name, 0) >= self.polling_interval:
                try:
                    attr_value = self.device.read_attribute(attr_name)
                    data[attr_name] = {
                        'value': attr_value.value,
                        'quality': attr_value.quality,
                        'timestamp': attr_value.time.totime() if hasattr(attr_value.time, 'totime') else time.time()
                    }
                    self.last_poll_time[attr_name] = current_time
                except Exception as e:
                    st.error(f"Ошибка чтения {attr_name}: {e}")

        return data

    def get_available_attributes(self):
        try:
            if self.device:
                return self.device.get_attribute_list()
            return []
        except:
            return []


def main():
    st.title("📊 BUK-M1 Real-time Monitor")

    # Инициализация в session state
    if 'monitor' not in st.session_state:
        st.session_state.monitor = TangoPollingMonitor("test/BUK_M1/2")
        st.session_state.attribute_data = {}
        st.session_state.last_poll_time = 0

    monitor = st.session_state.monitor

    # Сайдбар
    with st.sidebar:
        st.header("⚙️ Управление")

        if st.button("🔌 Подключиться"):
            if monitor.connect():
                st.success("✅ Подключено!")
                st.rerun()

        if monitor.device:
            attrs = monitor.get_available_attributes()
            current_attrs = [a for a in attrs if any(
                x in a.lower() for x in ['current', 'voltage', 'temp'])]

            selected = st.multiselect(
                "Атрибуты для мониторинга:",
                current_attrs,
                default=current_attrs[:3] if current_attrs else []
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Добавить"):
                    for attr in selected:
                        monitor.subscribe_to_attribute(attr)
                    st.rerun()

            with col2:
                if st.button("🗑️ Очистить"):
                    monitor.subscribed_attrs.clear()
                    st.session_state.attribute_data.clear()
                    st.rerun()

            st.divider()
            st.write(f"📊 Отслеживается: {len(monitor.subscribed_attrs)}")

    # Основная область
    # Опрос данных
    current_time = time.time()
    if monitor.device and monitor.subscribed_attrs and current_time - st.session_state.last_poll_time >= 1.0:
        new_data = monitor.poll_attributes()

        for attr_name, data in new_data.items():
            if attr_name not in st.session_state.attribute_data:
                st.session_state.attribute_data[attr_name] = []

            st.session_state.attribute_data[attr_name].append({
                'value': data['value'],
                'timestamp': data['timestamp']
            })

            # Ограничиваем историю
            if len(st.session_state.attribute_data[attr_name]) > 50:
                st.session_state.attribute_data[attr_name].pop(0)

        st.session_state.last_poll_time = current_time

    # Отображение графиков
    if st.session_state.attribute_data:
        # Создаем графики
        fig = make_subplots(
            rows=len(st.session_state.attribute_data),
            cols=1,
            subplot_titles=list(st.session_state.attribute_data.keys()),
            vertical_spacing=0.15
        )

        for i, (attr_name, data) in enumerate(st.session_state.attribute_data.items()):
            if data:
                x = [d['timestamp'] for d in data]
                y = [d['value'] for d in data]

                # Преобразуем время в читаемый формат
                x_dates = [time.strftime(
                    '%H:%M:%S', time.localtime(ts)) for ts in x]

                fig.add_trace(
                    go.Scatter(
                        x=x_dates,
                        y=y,
                        name=attr_name,
                        mode='lines+markers',
                        line=dict(width=2)
                    ),
                    row=i+1, col=1
                )

        fig.update_layout(
            height=min(800, len(st.session_state.attribute_data) * 200),
            showlegend=False,
            title_text="Мониторинг атрибутов BUK-M1"
        )

        # Настройка осей времени
        for i in range(len(st.session_state.attribute_data)):
            fig.update_xaxes(title_text="Время", row=i+1, col=1)

        st.plotly_chart(fig, use_container_width=True)

        # Таблица текущих значений
        st.subheader("📋 Текущие значения")
        current_values = []

        for attr_name, data in st.session_state.attribute_data.items():
            if data:
                latest = data[-1]
                current_values.append({
                    'Атрибут': attr_name,
                    'Значение': latest['value'],
                    'Время': time.strftime('%H:%M:%S', time.localtime(latest['timestamp']))
                })

        if current_values:
            df = pd.DataFrame(current_values)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Нет данных. Добавьте атрибуты для мониторинга.")

    # Кнопка обновления
    if st.button("🔄 Обновить сейчас"):
        st.rerun()

    # Автообновление
    auto_refresh = st.checkbox("🔄 Автообновление", value=True)
    if auto_refresh:
        time.sleep(1)
        st.rerun()


if __name__ == "__main__":
    main()
