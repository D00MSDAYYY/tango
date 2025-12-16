import tango
import time
import signal
import sys
import numpy as np


def main():
    # Флаг для graceful shutdown
    running = True

    def signal_handler(sig, frame):
        """Обработчик сигналов для graceful shutdown"""
        nonlocal running
        print(f"\nПолучен сигнал {sig}, завершаю работу...")
        running = False

    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill команда

    # Подключение к устройству
    print("Подключение к Tango устройству...")
    try:
        proxy = tango.DeviceProxy("test/power_supply/1")
        print(f"Подключено к {proxy.name()}")
        print(f"Ping: {proxy.ping()} мс")
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        sys.exit(1)

    # Включаем pulse mode если нужно
    try:
        proxy.enable_pulse_mode = True
        time.sleep(2)
        print("Pulse mode включен")
    except Exception as e:
        print(f"Не удалось включить pulse mode: {e}")

    # Статистика
    event_count = 0
    error_count = 0

    # Обработчик событий - ИСПРАВЛЕННЫЙ
    def event_handler(event_data):
        nonlocal event_count, error_count

        event_count += 1

        if event_data.err:
            error_count += 1
            print(f"\n[ERROR #{error_count}] {event_data.errors[0].desc[:100]}")
        else:
            # Безопасная обработка данных
            data = event_data.attr_value.value

            if data is None:
                print(f"\n[EVENT #{event_count}] Данные: None")
                return

            print(f"\n[EVENT #{event_count}] Получены данные")
            print(f"  Тип: {type(data).__name__}")

            if isinstance(data, list):
                size = len(data)
                print(f"  Размер списка: {size}")

                if size > 0:
                    if isinstance(data[0], list):
                        # Двумерный список
                        col_count = len(data[0]) if data[0] else 0
                        print(f"  Двумерный: {size} строк x {col_count} столбцов")
                        if size > 0 and col_count > 0:
                            print(f"  Первая строка (первые 3): {data[0][:3]}...")
                    else:
                        # Одномерный список
                        print(f"  Первые 5 значений: {data[:5]}")

            elif isinstance(data, tuple):
                # Кортеж
                size = len(data)
                print(f"  Размер кортежа: {size}")
                if size > 0:
                    print(f"  Первые 5 значений: {data[:5]}")

            elif isinstance(data, np.ndarray):
                # Numpy array
                print(f"  Numpy shape: {data.shape}")
                print(f"  Numpy dtype: {data.dtype}")
                if len(data.shape) == 1 and data.shape[0] > 0:
                    print(f"  Первые 5 значений: {data[:5]}")
                elif len(data.shape) == 2 and data.shape[0] > 0 and data.shape[1] > 0:
                    print(data)

            elif isinstance(data, str):
                # Строка
                if len(data) > 100:
                    print(f"  Строка (первые 100 симв): {data[:100]}...")
                else:
                    print(f"  Строка: {data}")

            else:
                # Другой тип
                try:
                    str_repr = str(data)
                    if len(str_repr) > 100:
                        print(f"  Значение: {str_repr[:100]}...")
                    else:
                        print(f"  Значение: {str_repr}")
                except:
                    print(f"  Значение: [не удалось преобразовать]")

    # Подписка на события
    print("\nПодписка на события...")
    try:
        event_id = proxy.subscribe_event(
            "pulse_mode_values", tango.EventType.PERIODIC_EVENT, event_handler
        )
        print(f"Подписка успешна, ID: {event_id}")
    except Exception as e:
        print(f"Ошибка подписки: {e}")
        sys.exit(1)

    # Основной бесконечный цикл
    print("\n" + "=" * 50)
    print("Клиент запущен. Нажмите Ctrl+C для остановки.")
    print("=" * 50 + "\n")

    last_stats_time = time.time()

    try:
        while running:
            # Вывод статистики каждые 10 секунд
            current_time = time.time()
            if current_time - last_stats_time > 10:
                print(f"\n[СТАТИСТИКА] Событий: {event_count}, Ошибок: {error_count}")
                last_stats_time = current_time

            # Короткая пауза чтобы не грузить CPU
            time.sleep(0.1)

    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

    finally:
        # Cleanup
        print("\n" + "=" * 50)
        print("Завершение работы...")

        try:
            proxy.unsubscribe_event(event_id)
            print("Отписался от событий")
        except:
            pass

        try:
            proxy.enable_pulse_mode = False
            print("Выключил pulse mode")
        except:
            pass

        print(f"Итоговая статистика: {event_count} событий, {error_count} ошибок")
        print("Клиент остановлен.")


if __name__ == "__main__":
    main()
