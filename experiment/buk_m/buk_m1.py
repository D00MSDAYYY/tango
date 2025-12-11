from .buk_m import BUK_M
from collections import deque
from tango.server import attribute, command, AttrWriteType
from typing import Deque
from threading import Lock


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

    # ########################################################################################

    def init_device(self):
        print("-> BUK_M1")

        super().init_device()
        self.stop_polling()

        print("<- BUK_M1")

    # ########################################################################################

    def initialize_dynamic_attributes(self):
        # fmt: off
        attribute_configs = [
                ('supplier_status',                 str,    self._supplier_status_read_FACTORY,                    "Статус источника тока"),
                ('error_warning',                   str,    self._error_warning_read_FACTORY,                      "Ошибки/предупреждения"),
                ('output_current_float',            float,  self._output_current_float_read_FACTORY,               "Выходной ток"),
                ('load_current_float',              float,  self._load_current_float_read_FACTORY,                 "Ток в нагрузке"),
                ('load_voltage_float',              float,  self._load_voltage_float_read_FACTORY,                 "Напряжение в нагрузке"),
                ('temp_modulator_transistors_float',float,  self._temp_modulator_transistors_float_read_FACTORY,   "Температура транзисторов"),
                ('temp_inductor_float',             float,  self._temp_inductor_float_read_FACTORY,                "Температура дросселя"),
                ('setpoint_output_current_float',   float,  self._setpoint_output_current_float_read_FACTORY,      "Уставка выходного тока")
        ]
        # fmt: on
        for i in range(1, self._CURRENT_SUPPLIERS_NUMBER):
            for (
                attr_name,
                dtype,
                factory,
                # period,
                # pol_period,
                doc_str,
            ) in attribute_configs:
                attr_obj = attribute(
                    name=f"{attr_name}_{i}",
                    dtype=dtype,
                    access=AttrWriteType.READ,
                    fget=factory(i),
                    doc=f"{doc_str} #{i}",
                )
                self.add_attribute(attr_obj)

    # ########################################################################################

    def _supplier_status_read_FACTORY(self, modbus_id):
        def _(self, attr):
            print("_supplier_status_read_FACTORY ")
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

        def _(self, attr):
            print("_error_warning_read_FACTORY  ")

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

        def _(self, attr):
            return self._convert_to_float32(
                self._read_input_registers(
                    self._REGISTER_OUTPUT_CURRENT_FLOAT, 2, modbus_id
                )
            )

        return _

    # ########################################################################################

    def _load_current_float_read_FACTORY(self, modbus_id):

        def _(self, attr):
            return self._convert_to_float32(
                self._read_input_registers(
                    self._REGISTER_LOAD_CURRENT_FLOAT, 2, modbus_id
                )
            )

        return _

    # ########################################################################################

    def _load_voltage_float_read_FACTORY(self, modbus_id):

        def _(self, attr):
            return self._convert_to_float32(
                self._read_input_registers(
                    self._REGISTER_LOAD_VOLTAGE_FLOAT, 2, modbus_id
                )
            )

        return _

    # ########################################################################################

    def _temp_modulator_transistors_float_read_FACTORY(self, modbus_id):

        def _(self, attr):
            return self._convert_to_float32(
                self._read_input_registers(
                    self._REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT, 2, modbus_id
                )
            )

        return _

    # ########################################################################################

    def _temp_inductor_float_read_FACTORY(self, modbus_id):

        def _(self, attr):
            return self._convert_to_float32(
                self._read_input_registers(self._REGISTER_INDUCTOR_FLOAT, 2, modbus_id)
            )

        return _

    # ########################################################################################

    def _setpoint_output_current_float_read_FACTORY(self, modbus_id):

        def _(self, attr):
            return self._convert_to_float32(
                self._read_input_registers(
                    self._REGISTER_SETPOINT_CURRENT_FLOAT, 2, modbus_id
                )
            )

        return _

    # ########################################################################################

    # def _process_pulse_mode_packet(self, data: bytes, addr: tuple):
    #     """Обработка Pulse пакета"""
    #     import struct

    # # fmt: off
    #     try:
    #         expected_size = (4	#	cостояние, тип числа int32
    #         + 4 				#	счетчик пакетов, тип числа int32
    #         + 8 				#	время отправки пакета в секундах с начала «эпохи», тип числа double
    #         + (8 * 8) 			#	массив из 8ми чисел с показаниями токов, тип числа double
    #         + (8 * 8)) 			#	массив из 8ми чисел с показаниями напряжений, тип числа double

    #         if len(data) != expected_size:
    #             raise ValueError(f"Неверный размер пакета: {len(data)} байт, ожидается {expected_size} байт")

    #         fmt = '>2i d 16d'	# 2 int32 + 1 double + 16 double
    #         unpacked_data = struct.unpack(fmt, data)

    #         currents = self.modbus_client.convert_from_registers(
    #             unpacked_data[3:(3 + self._CURRENT_SUPPLIERS_NUMBER)],
    #             data_type=self.modbus_client.DATATYPE.FLOAT64)    # 8 значений токов

    #         voltages = self.modbus_client.convert_from_registers(
    #            unpacked_data[11:(11 + self._CURRENT_SUPPLIERS_NUMBER)],
    #             data_type=self.modbus_client.DATATYPE.FLOAT64)    # 8 значений напряжений
    # # fmt: on

    #         decoded_data = {
    #             'state': unpacked_data[0],
    #             'packet_counter': unpacked_data[1],
    #             'timestamp': unpacked_data[2],
    #             'currents': currents,
    #             'voltages': voltages
    #         }
    #         print('decoded data: ', decoded_data)

    #         self._packet_buffer.append(decoded_data)

    #         for i, (current, voltage) in enumerate(zip(currents, voltages)):
    #             self.get_attribute_by_name(
    #                 f"load_current_float_{i}").set_value(current)
    #             self.get_attribute_by_name(
    #                 f"load_voltage_float_{i}").set_value(voltage)

    #     except Exception as e:
    #         print(f"Ошибка обработки Pulse пакета БУК-М1 : {e}")

    #
    # fmt: off
    PULSE_MODE_POLLING_PERIOD_EPSILON_MS:int    = 300
    PULSE_MODE_EVENT_PERIOD_MS:int              = 1000
    PULSE_MODE_ARRAY_SIZE:int                   = int(PULSE_MODE_EVENT_PERIOD_MS / PULSE_MODE_POLLING_PERIOD_EPSILON_MS)
    PULSE_MODE_DUMMY_ARRAY: Deque[float]        = deque(maxlen=1000)
    # fmt: on

    # ########################################################################################

    _pulse_mode_values_lock: Lock = Lock()

    # ########################################################################################

    _enable_pulse_mode: bool = False

    # ########################################################################################

    _pulse_mode_values: list[list[float]]

    # ########################################################################################

    _stash: list[list[float]]

    # ########################################################################################

    _aux_attr_for_polling = attribute(
        label="_aux_attr_for_polling",
        dtype=str,
        doc="костыль, нужный для работы pulse mode. не подписывайтесь и не читайте его!!!",
    )

    # ########################################################################################

    @_aux_attr_for_polling.read
    def _(self):
        print("in _aux_attr_for_polling.read ")

        values = []
        for attr_name, dtype, read_function, doc in (
            self.pulse_mode_attributes_configs or []
        ):
            try:
                attr_value = read_function(self, None)
            except Exception as e:
                print(e)
            print(attr_name, "\t\t\t\t", attr_value)

            values.append(attr_value)

        self._stash.append(values)
        if len(self._stash) >= self.PULSE_MODE_ARRAY_SIZE:
            with self._pulse_mode_values_lock:
                self._pulse_mode_values = self._stash
                self._stash = list()

    ########################################################################################

    # enable_pulse_mode = attribute(
    #     label="enable pulse mode", dtype=bool, doc="Pulse mode ON(1)/OFF(0) атрибут"
    # )

    # # # ########################################################################################

    # @enable_pulse_mode.read
    # def _(self):
    #     return self._enable_pulse_mode

    # # ########################################################################################

    # @enable_pulse_mode.write
    # def _(self, flag: bool):
    #     print("in enable_pulse_mode.write ")
    #     self._enable_pulse_mode = flag
    #     if self._enable_pulse_mode == True:
    #         self.poll_attribute(
    #             "_aux_attr_for_polling", self.PULSE_MODE_POLLING_PERIOD_EPSILON_MS
    #         )
    #     else:
    #         self.stop_poll_attribute("_aux_attr_for_polling")

    # # ########################################################################################
    pulse_mode_values = attribute(
        label="pulse_mode_values",
        dtype=float,
        max_dim_x=20,
        max_dim_y=2000,
        doc="атрибут, где хранится массив значений напряжений",
        period=1000,
    )

    # ########################################################################################

    @pulse_mode_values.read
    def _(self):
        print("\nin pulse_mode_values.read\n")
        if self._enable_pulse_mode:
            with self._pulse_mode_values_lock:
                result = list(self._pulse_mode_values)
                return result
        else:
            return self.PULSE_MODE_DUMMY_ARRAY

    # # ########################################################################################
