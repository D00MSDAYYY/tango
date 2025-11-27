import streamlit as st
import pytango
import time
import threading
import pandas as pd
from datetime import datetime

# Конфигурация
DEVICE_PROXY_FULLNAME = "my/device/proxy"  # Замените на ваш Tango device proxy
POLLING_INTERVAL = 2  # Интервал опроса в секундах
ATTRIBUTES_TO_POLL = ["attribute1", "attribute2",
                      "attribute3"]  # Замените на нужные атрибуты


class TangoPolling:
    def __init__(self):
        self.device = None
        self.is_running = False
        self.polling_thread = None
        self.data = []
        self.lock = threading.Lock()

    def connect(self):
        """Подключение к Tango устройству"""
        try:
            self.device = pytango.DeviceProxy(DEVICE_PROXY_FULLNAME)
            self.device.ping()  # Проверка соединения
            return True
        except pytango.DevFailed as e:
            st.error(f"Ошибка подключения к устройству: {e}")
            return False

    def poll_attributes(self):
        """Опрос атрибутов устройства"""
        if not self.device:
            return None

        try:
            result = {}
            for attr in ATTRIBUTES_TO_POLL:
                value = self.device.read_attribute(attr).value
                result[attr] = value
            result['timestamp'] = datetime.now()
            return result
        except pytango.DevFailed as e:
            st.error(f"Ошибка чтения атрибутов: {e}")
            return None

    def start_polling(self):
        """Запуск периодического опроса в отдельном потоке"""
        if not self.connect():
            return False

        self.is_running = True
        self.polling_thread = threading.Thread(target=self._polling_worker)
        self.polling_thread.daemon = True
        self.polling_thread.start()
        return True

    def stop_polling(self):
        """Остановка опроса"""
        self.is_running = False
        if self.polling_thread:
            self.polling_thread.join(timeout=1.0)

    def _polling_worker(self):
        """Рабочий поток для периодического опроса"""
        while self.is_running:
            data_point = self.poll_attributes()
            if data_point:
                with self.lock:
                    self.data.append(data_point)
                    # Сохраняем только последние 100 записей
                    if len(self.data) > 100:
                        self.data.pop(0)
            time.sleep(POLLING_INTERVAL)

    def get_latest_data(self):
        """Получение последних данных"""
        with self.lock:
            return self.data.copy()

    def clear_data(self):
        """Очистка данных"""
        with self.lock:
            self.data.clear()


# Создаем экземпляр опроса
if 'tango_polling' not in st.session_state:
    st.session_state.tango_polling = TangoPolling()


def main():
    st.title("Tango Device Monitor")
    st.write("Мониторинг Tango устройства через PyTango")

    # Управление опросом
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Запуск опроса", type="primary"):
            if st.session_state.tango_polling.start_polling():
                st.success("Опрос запущен")
            else:
                st.error("Не удалось запустить опрос")

    with col2:
        if st.button("Остановка опроса"):
            st.session_state.tango_polling.stop_polling()
            st.info("Опрос остановлен")

    with col3:
        if st.button("Очистить данные"):
            st.session_state.tango_polling.clear_data()
            st.info("Данные очищены")

    st.divider()

    # Отображение текущих данных
    st.subheader("Текущие значения")

    latest_data = st.session_state.tango_polling.get_latest_data()
    if latest_data:
        # Последняя запись
        latest = latest_data[-1]

        # Отображение в колонках
        cols = st.columns(len(ATTRIBUTES_TO_POLL) + 1)

        with cols[0]:
            st.metric("Время", latest['timestamp'].strftime("%H:%M:%S"))

        for i, attr in enumerate(ATTRIBUTES_TO_POLL, 1):
            with cols[i]:
                st.metric(attr, f"{latest[attr]:.3f}")

    # График истории
    st.subheader("История значений")

    if len(latest_data) > 1:
        # Создаем DataFrame для графика
        df = pd.DataFrame(latest_data)
        df.set_index('timestamp', inplace=True)

        # Отображаем график
        st.line_chart(df)

        # Таблица с данными
        st.subheader("Таблица данных")
        st.dataframe(df.tail(10))  # Показываем последние 10 записей

        # Кнопка для экспорта данных
        if st.button("Экспорт данных в CSV"):
            csv = df.to_csv()
            st.download_button(
                label="Скачать CSV",
                data=csv,
                file_name=f"tango_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Нет данных для отображения. Запустите опрос.")

    # Информация о состоянии
    st.sidebar.header("Информация")
    st.sidebar.write(f"Устройство: {DEVICE_PROXY_FULLNAME}")
    st.sidebar.write(f"Интервал опроса: {POLLING_INTERVAL} сек")
    st.sidebar.write(
        f"Статус: {'Запущен' if st.session_state.tango_polling.is_running else 'Остановлен'}")
    st.sidebar.write(f"Количество записей: {len(latest_data)}")


if __name__ == "__main__":
    main()
