from tango import DeviceProxy, EventType
import time


class BUK_M1_Client:
    def __init__(self, device_name):
        self.device = DeviceProxy(device_name)
        
    def print_all_measurements(self):
        """Вывести все измерения для всех источников"""
        print(self.get_attribute_list())
        
        print("теперь только токи : ")
        for i in range(8):  # 8 источников тока
            try:
                current = self.device.read_attribute(f"load_current_float_{i}").value
                voltage = self.device.read_attribute(f"load_voltage_float_{i}").value
                status = self.device.read_attribute(f"status_{i}").value
                
                print(f"Источник {i}: {status}")
                print(f"  Ток: {current:.3f} A, Напряжение: {voltage:.3f} V")
                
            except Exception as e:
                print(f"Ошибка чтения источника {i}: {e}")
            
    
    def monitor_changes(self, duration=60):
        """Мониторинг изменений в реальном времени"""
        def current_callback(event):
            if not event.err:
                print(f"📈 Изменение тока {event.attr_name}: {event.attr_value.value:.3f}A")
        
        # Подписка на изменения токов
        for i in range(8):
            self.device.subscribe_event(
                f"load_current_float_{i}",
                EventType.CHANGE_EVENT,
                current_callback
            )
        
        print(f"Мониторинг запущен на {duration} секунд...")
        time.sleep(duration)

# Использование
client = BUK_M1_Client("my/buk-m1/device/1")
client.print_all_measurements()
client.monitor_changes()