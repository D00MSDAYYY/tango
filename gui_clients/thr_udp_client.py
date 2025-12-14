from tango import DeviceProxy
import time

# Подключаемся к устройству
dev_proxy = DeviceProxy("test/BUK_M1/1")
print("✅ Подключено к устройству")

# Получаем список всех атрибутов
all_attributes = dev_proxy.get_attribute_list()
print(f"📋 Всего атрибутов: {len(all_attributes)}")

# Выбираем атрибуты тока и напряжения для демонстрации
current_voltage_attrs = [attr for attr in all_attributes 
                        if 'current' in attr or 'voltage' in attr][:4]

print(f"🎯 Демо атрибуты: {current_voltage_attrs}")

# Подписываемся на атрибуты
print("📝 Подписка на атрибуты...")
results = dev_proxy.subscribe(502, current_voltage_attrs)

for attr, success in zip(current_voltage_attrs, results):
    status = "✅ Успешно" if success else "❌ Ошибка"
    print(f"   {attr}: {status}")

# Ждем некоторое время (в реальности здесь будут приходить данные по TCP)
print("\n⏳ Ожидание данных 10 секунд...")
time.sleep(10)

# Читаем текущие значения атрибутов
print("\n📖 Текущие значения атрибутов:")
for attr in current_voltage_attrs:
    try:
        value = dev_proxy.read_attribute(attr).value
        print(f"   {attr}: {value}")
    except Exception as e:
        print(f"   {attr}: ❌ Ошибка - {e}")

# Отписываемся
print("\n🛑 Отписка от атрибутов...")
unsubscribe_results = dev_proxy.unsubscribe(502, current_voltage_attrs)

for attr, success in zip(current_voltage_attrs, unsubscribe_results):
    status = "✅ Успешно" if success else "❌ Ошибка"
    print(f"   {attr}: {status}")

print("👋 Готово!")