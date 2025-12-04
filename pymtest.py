try:
    # Пробуем новый API (3.x)
    from pymodbus import Endian
    from pymodbus.convert_to import BinaryPayloadDecoder
    print("Используется pymodbus 3.x")
except ImportError:
    try:
        # Пробуем старый API (2.x)
        from pymodbus.constants import Endian
        from pymodbus.payload import BinaryPayloadDecoder
        print("Используется pymodbus 2.x")
    except ImportError:
        print("Не удалось импортировать pymodbus")
        raise
