import json
import socket
import time

from buk_m import BUK_M
from collections import deque
from tango.server import attribute, command, AttrWriteType
from tango._tango import ClientAddr
from typing import List, Tuple, Dict
from types import SimpleNamespace


class BUK_M1(BUK_M):

    # ########################################################################################

    _REGISTER_STATUS_WORD = 300001
    _REGISTER_ERROR_WARNING = 300002
    _REGISTER_OUTPUT_CURRENT_FLOAT = 300003
    _REGISTER_LOAD_CURRENT_FLOAT = 300005
    _REGISTER_LOAD_VOLTAGE_FLOAT = 300007
    _REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT = 300009
    _REGISTER_INDUCTOR_FLOAT = 300011
    _REGISTER_SETPOINT_CURRENT_FLOAT = 300013

    _MAX_PACKETS_BUFFER_SIZE = 1000

    _CURRENT_SUPPLIERS_NUMBER = 8

    # ########################################################################################

    DEVICE_CLASS_DESCRIPTION = "БУК-М1. Источники тока корректоров"

    _packet_buffer = deque(maxlen=_MAX_PACKETS_BUFFER_SIZE)

    _subscriptions: Dict[str, List[Tuple[dict[str, int], float]]]

    # ########################################################################################

    def init_device(self):
        print("-> BUK_M1")

        super().init_device()

        print("<- BUK_M1")

    # ########################################################################################

    def initialize_dynamic_attributes(self):
        # fmt: off
        attribute_configs = [
                ('supplier_status', 				str, 	self._supplier_status_read_FACTORY,                 "",      -1,   "Статус источника тока"),
                ('error_warning', 					str, 	self._error_warning_read_FACTORY,                   3000,   3000,   "Ошибки/предупреждения"),
                ('output_current_float', 			float, 	self._output_current_float_read_FACTORY,            1000,   1000,  "Выходной ток"),
                ('load_current_float', 				float, 	self._load_current_float_read_FACTORY,              1000,   1000,   "Ток в нагрузке"),
                ('load_voltage_float', 				float, 	self._load_voltage_float_read_FACTORY,              1000,   1000,   "Напряжение в нагрузке"),
                ('temp_modulator_transistors_float',float, 	self._temp_modulator_transistors_float_read_FACTORY,1000,   1000,   "Температура транзисторов"),
                ('temp_inductor_float', 			float, 	self._temp_inductor_float_read_FACTORY,             1000,   1000,   "Температура дросселя"),
                ('setpoint_output_current_float', 	float, 	self._setpoint_output_current_float_read_FACTORY,   1000,   1000,   "Уставка выходного тока")
        ]
        # fmt: on
        for i in range(self._CURRENT_SUPPLIERS_NUMBER):
            for attr_name, dtype, factory, period, pol_period, doc_str in attribute_configs:
                attr_obj = attribute(
                    name=f"{attr_name}_{i}",
                    dtype=dtype,
                    access=AttrWriteType.READ,
                    fget=factory(i),
                    doc=f"{doc_str} #{i}",
                    period=period,
                    polling_period=pol_period
                )
                self.add_attribute(attr_obj)

    # ########################################################################################

    def _supplier_status_read_FACTORY(self, modbus_id):
        def _(self, _) -> str:
            result = self._read_input_registers(
                self._REGISTER_STATUS_WORD, 1, modbus_id
            )

            if result is None:
                return "Ошибка чтения статуса источника"

            status_bits = format(result[0], "016b")[::-1]

            # print(
            #     f"Статус источника: {status_bits} из регистра {self._REGISTER_STATUS_WORD}"
            # )

            state_map = {
                (0, 0): "отключен",
                (1, 0): "штатная работа",
                (0, 1): "останов в безопасном режиме",
                (1, 1): "режим прямого управления ШИМ",
            }

            state_key = (int(status_bits[1]), int(status_bits[0]))

            response_str = state_map.get(state_key, "неизвестное состояние")

            if int(status_bits[2]):
                response_str += ", инициализирован"
            else:
                response_str += ", неинициализирован"

            return response_str

        return _

    # ########################################################################################

    def _error_warning_read_FACTORY(self, modbus_id):
        def _(self, _):
            result = self._read_input_registers(
                self._REGISTER_ERROR_WARNING, 1, modbus_id
            )

            if result is None:
                return "Ошибка чтения статуса источника"

            status_bits = format(result[0], "016b")[::-1]

            print(f"Ошибки\\предупреждения источника: {status_bits}")

            return status_bits  # TODO добавить расшифровку

        return _

    # ########################################################################################

    def _output_current_float_read_FACTORY(self, modbus_id):
        def _(self, _):
            return self._read_float32_from_input_register(
                self._REGISTER_OUTPUT_CURRENT_FLOAT, modbus_id
            )

        return _

    # ########################################################################################

    def _load_current_float_read_FACTORY(self, modbus_id):
        def _(self, _):
            return self._read_float32_from_input_register(
                self._REGISTER_LOAD_CURRENT_FLOAT, modbus_id
            )

        return _

    # ########################################################################################

    def _load_voltage_float_read_FACTORY(self, modbus_id):
        def _(self, _):
            return self._read_float32_from_input_register(
                self._REGISTER_LOAD_VOLTAGE_FLOAT, modbus_id
            )

        return _

    # ########################################################################################

    def _temp_modulator_transistors_float_read_FACTORY(self, modbus_id):
        def _(self, _):
            return self._read_float32_from_input_register(
                self._REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT, modbus_id
            )

        return _

    # ########################################################################################

    def _temp_inductor_float_read_FACTORY(self, modbus_id):
        def _(self, _):
            return self._read_float32_from_input_register(
                self._REGISTER_INDUCTOR_FLOAT, modbus_id
            )

        return _

    # ########################################################################################

    def _setpoint_output_current_float_read_FACTORY(self, modbus_id):
        def _(self, _):
            return self._read_float32_from_input_register(
                self._REGISTER_SETPOINT_CURRENT_FLOAT, modbus_id
            )

        return _

    # ########################################################################################

    def _process_pulse_mode_packet(self, data: bytes, addr: tuple):
        """Обработка Pulse пакета"""
        import struct

        # fmt: off
        try:
            expected_size = (4	#	cостояние, тип числа int32
            + 4 				#	счетчик пакетов, тип числа int32
            + 8 				#	время отправки пакета в секундах с начала «эпохи», тип числа double
            + (8 * 8) 			#	массив из 8ми чисел с показаниями токов, тип числа double
            + (8 * 8)) 			#	массив из 8ми чисел с показаниями напряжений, тип числа double

            if len(data) != expected_size:
                raise ValueError(f"Неверный размер пакета: {len(data)} байт, ожидается {expected_size} байт")

            fmt = '>2i d 16d'	# 2 int32 + 1 double + 16 double
            unpacked_data = struct.unpack(fmt, data)

            currents = unpacked_data[3:(3 + self._CURRENT_SUPPLIERS_NUMBER)]   # 8 значений токов
            voltages = unpacked_data[11:(11 + self._CURRENT_SUPPLIERS_NUMBER)]  # 8 значений напряжений
# fmt: on
            decoded_data = {
                'state': unpacked_data[0],
                'packet_counter': unpacked_data[1],
                'timestamp': unpacked_data[2],
                'currents': list(currents),
                'voltages': list(voltages)
            }
            print('decoded data: ', decoded_data)

            self._packet_buffer.append(decoded_data)

            for i, (current, voltage) in enumerate(zip(currents, voltages)):
                self._send_to_subscribers(f"load_current_float_{i}", current)
                self._send_to_subscribers(f"load_voltage_float_{i}", voltage)

        except Exception as e:
            print(f"Ошибка обработки Pulse пакета БУК-М1 : {e}")

    # ########################################################################################

    @command
    def subscribe(self, passed_port, attr_names):
        def _subscribe_to_attribute(attr_name):
            if attr_name not in self.get_device_attr().get_attr_list():
                self.error_stream(f"Attribute {attr_name} does not exist")
                return False

            client_addr = {"host": self.get_client_ident().client_ip,
                           "port": passed_port}

            last_request = time.time()
            self._subscriptions[attr_name].remove((client_addr, last_request))
            self._subscriptions[attr_name].append((client_addr, last_request))
            self.info_stream(
                f"Subscription timestamp updated for {client_addr["host"]}:{client_addr["port"]}"
            )
            return True

        results = []

        for attr_name in attr_names:
            is_success = _subscribe_to_attribute(attr_name)
            results.append(is_success)

        return results

    ########################################################################################

    @command
    def unsubscribe(self, passed_port, attr_names):

        def _unsubscribe_from_attribute(attr_name):
            if attr_name not in self.get_device_attr().get_attr_list():
                self.error_stream(f"Attribute {attr_name} does not exist")
                return False

            client_addr = {"host": self.get_client_ident().client_ip,
                           "port": passed_port}

            if attr_name not in self._subscriptions:
                self.error_stream(
                    f"No subscriptions found for attribute {attr_name}")
                return False

            for sub_list_item in self._subscriptions[attr_name]:
                subber, _ = sub_list_item
                if subber["host"] == client_addr["host"] and subber["port"] == client_addr["port"]:
                    self._subscriptions[attr_name].remove(sub_list_item)
                    # Если больше нет подписок для этого атрибута, удаляем запись
                    if not self._subscriptions[attr_name]:
                        del self._subscriptions[attr_name]
                        self.info_stream(
                            f"No more subscriptions for {attr_name}, cleaned up"
                        )
                    return True

            return False

        results = []

        for attr_name in attr_names:
            is_success = _unsubscribe_from_attribute(attr_name)
            results.append(is_success)

        return results

    ########################################################################################

    def _send_to_subscribers(self, attr_name, value):
        """
        Отправляет значение всем подписчикам атрибута
        """
        if attr_name not in self._subscriptions:
            return  # Нет подписчиков для этого атрибута

        current_time = time.time()
        subscribers_to_remove = []

        for sub_list_item in self._subscriptions[attr_name]:
            client_addr, subscribe_time = sub_list_item

            # Проверяем не устарела ли подписка (например, больше 1 часа)
            if current_time - subscribe_time > 3600:  # 1 час в секундах
                subscribers_to_remove.append(sub_list_item)
                continue

            try:
                # Отправляем значение подписчику
                self._send_value_to_client(client_addr, attr_name, value)

            except Exception as e:
                self.error_stream(
                    f"Failed to send to {client_addr["host"]}:{client_addr["port"]}: {e}"
                )
                subscribers_to_remove.append(sub_list_item)

        # Удаляем неактивных подписчиков
        for sub_list_item in subscribers_to_remove:
            self._subscriptions[attr_name].remove(sub_list_item)
            client_addr, _ = sub_list_item
            self.info_stream(
                f"Removed inactive subscriber {client_addr.host}:{client_addr.port}"
            )

        # Очищаем пустые записи
        if not self._subscriptions[attr_name]:
            del self._subscriptions[attr_name]

    ########################################################################################

    def _send_value_to_client(self, client_addr, attr_name, value):
        """
        Отправляет значение через TCP сокет
        """
        try:
            # Создаем сокет
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)  # Таймаут 5 секунд

            # Подключаемся к клиенту
            sock.connect((client_addr.host, client_addr.port))

            # Формируем данные для отправки
            data = {
                "attribute": attr_name,
                "value": value,
                "timestamp": time.time(),
                "device": self.get_name(),
            }

            # Отправляем JSON
            message = json.dumps(data).encode("utf-8")
            sock.send(message)
            sock.close()

        except Exception as e:
            raise Exception(f"Socket error: {e}")
