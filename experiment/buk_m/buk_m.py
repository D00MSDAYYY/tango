import threading
import socket

from ._tango_modbus import _TANGO_MODBUS
from tango.server import class_property, command, attribute
from tango import Attribute
from abc import abstractmethod
from typing import Optional


class BUK_M(_TANGO_MODBUS):

    # ########################################################################################

    _REGISTER_STATUS_WORD = 300001
    _REGISTER_ERROR_WORD = 300002
    _REGISTER_ACCIDENT_WORD = 300003
    _REGISTER_COMMAND_WORD = 400001
    _REGISTER_PULSE_MODE = 400002

    _CODE_STOP = 1 << 1
    _CODE_GET_CYCLOGRAMM = 1 << 2
    _CODE_CANCEL_CYCLOGRAMM = 1 << 3
    _CODE_RESET_INITIALIZATION = 1 << 5
    _CODE_ACKNOWLEDGE_ERROR = 1 << 6
    _CODE_ACKNOWLEDGE_ACCIDENT = 1 << 7
    _CODE_RESET_INITIALIZATION_INCOMPLETE = 1 << 13

    # ########################################################################################

    DEVICE_CLASS_DESCRIPTION = "Блок управления и коммутации БУК-М"
    # адрес Modbus_ID корневого устройства
    MODBUS_ID_PARENT_BUK_M = class_property(dtype=int, default_value=0)

    # ########################################################################################

    def init_device(self):
        print('-> BUK_M')

        super().init_device()

        print('<- BUK_M')

    # ########################################################################################

    status = attribute(
        label="status",
        dtype=str,
        doc="Статус устройства БУК-М"
    )

    @status.read
    def _(self, attr):
        result = self._read_input_registers(
            self._REGISTER_STATUS_WORD, 1, self.MODBUS_ID_PARENT_BUK_M)

        if result is None:
            return "Ошибка чтения слова статуса"

        status_bits = format(result[0], '016b')[::-1]

        print(status_bits)

        status_map = {
            0: "Инициализация контроллера",
            1: "Загружен файл конфигурации",
            2: "Настройка оборудования",
            3: "Все системы инициализированы",
            4: "Циклограмма загружается",
            5: "Циклограмма получена и обработана",
            6: "Циклограмма выполняется",
            15: "Запись команд запрещена"
        }

        status = "Статус не определен"
        for bit_index, message in status_map.items():
            if int(status_bits[bit_index]):
                status = message

        return status

    # ########################################################################################

    def _do_command(self, comm_addr,  command_code, modbus_id):
        self.modbus_client.write_register(
            address=comm_addr - self._OFFSET_HOLDING_REGISTER,
            value=command_code,
            device_id=modbus_id
        )

    # ########################################################################################

    @command(doc_in="#TODO")
    def stop(self):
        return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_STOP, self.MODBUS_ID_PARENT_BUK_M)

    # ########################################################################################

    @command
    def get_cyclogram(self):
        return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_GET_CYCLOGRAMM, self.MODBUS_ID_PARENT_BUK_M)

    # ########################################################################################

    @command
    def cancel_cyclogram(self):
        return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_CANCEL_CYCLOGRAMM, self.MODBUS_ID_PARENT_BUK_M)

    # ########################################################################################

    @command
    def reset_initialization(self):
        return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_RESET_INITIALIZATION, self.MODBUS_ID_PARENT_BUK_M)

    # ########################################################################################

    @command
    def acknowledge_error(self):
        return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_ACKNOWLEDGE_ERROR, self.MODBUS_ID_PARENT_BUK_M)

    # ########################################################################################

    @command
    def acknowledge_accident(self):
        return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_ACKNOWLEDGE_ACCIDENT, self.MODBUS_ID_PARENT_BUK_M)

    # ########################################################################################

    @command
    def reset_initialization_incomplete(self):
        return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_RESET_INITIALIZATION_INCOMPLETE, self.MODBUS_ID_PARENT_BUK_M)

    errors = attribute(
        label="errors",
        dtype=str,
        doc="Слово ошибок"
    )

    @errors.read
    def errors_read(self):
        result = self._read_input_registers(
            self._REGISTER_ERROR_WORD, 1, self.MODBUS_ID_PARENT_BUK_M)

        if result is None:
            return "Ошибка чтения слова ошибок"

        errors_bits = format(result[0], '016b')[::-1]
        # print(f"Слово ошибок: {errors_bits}")

        errors_map = {
            0: "TFTP-сервер недоступен",
            1: "Ошибка открытия файла конфигурации",
            2: "Ошибка загрузки файла конфигурации",
            3: "Ошибка при инициализации модулей или устройств",
            4: "Ошибка установки соединения",
            5: "Ошибка загрузки циклограммы",
            6: "Ошибка обработки циклограммы",
            7: "Ошибка при выполнении циклограммы",
            8: "Ошибка",
            9: "Потеря связи с сервером",
            10: "Авария модуля",
            11: "Неверная команда",
            12: "Авария",
            13: "Ошибка IRIG"
        }

        active_errors = []
        for bit_index, message in errors_map.items():
            if errors_bits[bit_index] == '1':
                active_errors.append(message)

        return "; ".join(active_errors) if active_errors else "Ошибок нет"

    # ########################################################################################

    accidents = attribute(
        label="accidents",
        dtype=str,
        doc="Слово аварий"
    )

    @accidents.read
    def accidents_read(self):
        return "функция слова аварий пока не поддерживается"

    # ########################################################################################

    def get_attribute_by_name(self, attr_name: str) -> Optional[Attribute]:
        """
            Получить объект атрибута по имени

            Args:
                device: экземпляр Tango устройства
                attr_name: имя атрибута

            Returns:
                Объект атрибута или None если не найден
            """
        try:
            # Получаем DeviceAttribute объект
            device_attr = self.get_device_attr()

            # Получаем список всех атрибутов
            attributes = list(device_attr.get_attribute_list())

            # Ищем атрибут по имени
            for attr in attributes:
                if attr.get_name() == attr_name:
                    return attr

            return None
        except Exception as e:
            print(f"Ошибка при получении атрибута {attr_name}: {e}")
            return None
