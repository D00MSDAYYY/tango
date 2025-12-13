from .buk_m import BUK_M
from tango.server import attribute, AttrWriteType
from threading import Lock
import numpy as np

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

    # fmt: off
    PULSE_MODE_POLLING_PERIOD_EPSILON_MS:int    = 150
    PULSE_MODE_EVENT_PERIOD_MS:int              = 1000
    PULSE_MODE_ARRAY_SIZE:int                   = int(PULSE_MODE_EVENT_PERIOD_MS / PULSE_MODE_POLLING_PERIOD_EPSILON_MS)
    PULSE_MODE_DUMMY_ARRAY                      = np.zeros((0, 0), dtype=np.float32)
    # fmt: on

    # ########################################################################################

    _pulse_mode_values_lock: Lock = Lock()

    # ########################################################################################

    _enable_pulse_mode: bool = False

    # ########################################################################################

    _pulse_mode_values = np.zeros((0, 0), dtype=np.float32)

    # ########################################################################################

    _pulse_mode_values_stash = np.zeros((0, 0), dtype=np.float32)

    # ########################################################################################

    _aux_attr_for_polling = attribute(
        label="_aux_attr_for_polling",
        dtype=str,
        doc="костыль, нужный для работы pulse mode. не подписывайтесь и не читайте его!",
    )

    # ########################################################################################

    @_aux_attr_for_polling.read
    def _aux_attr_for_polling_read(self):
        # print("polling")

        # 1. Быстрая проверка состояния
        if not getattr(self, '_enable_pulse_mode', False):
            return 
        
        # 2. Проверка конфигурации
        configs = self.pulse_mode_attributes_configs
        if not configs:
            return "ERROR: No configs"

        # 3. Определение размеров
        num_values = len(configs)

        # 4. Создание массива NumPy для новых значений
        new_row = np.zeros(num_values, dtype=np.float32)

        # 5. Быстрое заполнение массива
        for i in range(num_values):
            _, _, read_function, _ = configs[i]
            try:
                new_row[i] = float(read_function(self, None))
            except (TypeError, ValueError):
                new_row[i] = 0.0  # Значение по умолчанию при ошибке

        # 6. Получение ссылки на stash
        stash = self._pulse_mode_values_stash

        # 7. Добавление новой строки в stash
        if stash.size == 0:
            # Первое добавление - создаем массив
            self._pulse_mode_values_stash = new_row.reshape(1, -1)
        else:
            # Добавляем новую строку к существующему массиву
            self._pulse_mode_values_stash = np.vstack([stash, new_row])

        # 8. Проверка размера и перенос данных
        if stash.shape[0] >= self.PULSE_MODE_ARRAY_SIZE:
            with self._pulse_mode_values_lock:
                # Создаем копию данных
                self._pulse_mode_values = stash.copy()

            # Очищаем stash, но оставляем последние N/4 строк для плавности
            keep_rows = max(1, self.PULSE_MODE_ARRAY_SIZE // 4)
            if stash.shape[0] > keep_rows:
                self._pulse_mode_values_stash = stash[-keep_rows:]
            else:
                # Создаем пустой массив с правильной размерностью столбцов
                self._pulse_mode_values_stash = np.zeros((0, num_values), dtype=np.float32)

    # ########################################################################################

    enable_pulse_mode = attribute(
        label="enable pulse mode", dtype=bool, doc="Pulse mode ON(1)/OFF(0) атрибут"
    )

    # ########################################################################################

    @enable_pulse_mode.read
    def enable_pulse_mode_read(self):
        return self._enable_pulse_mode

    # ########################################################################################

    @enable_pulse_mode.write
    def enable_pulse_mode_write(self, flag: bool):
        self._enable_pulse_mode = flag
        if flag == True:
            self.poll_attribute(
                "_aux_attr_for_polling", self.PULSE_MODE_POLLING_PERIOD_EPSILON_MS
            )
            self.poll_attribute(
                "pulse_mode_values", self.PULSE_MODE_POLLING_PERIOD_EPSILON_MS
            )
        else:
            self.stop_poll_attribute("_aux_attr_for_polling")
            self.stop_poll_attribute("pulse_mode_values")

    # # ########################################################################################

    pulse_mode_values = attribute(
        label="pulse_mode_values",
        dtype=((float,),),
        max_dim_x=30,
        max_dim_y=PULSE_MODE_ARRAY_SIZE,
        doc="атрибут, где хранится массив значений напряжений",
        period=1000,
    )

    # ########################################################################################

    @pulse_mode_values.read
    def pulse_mode_values_read(self):
        # print("\nin pulse_mode_values.read\n")
        if self._enable_pulse_mode:
            with self._pulse_mode_values_lock:
                return self._pulse_mode_values
        else:
            return self.PULSE_MODE_DUMMY_ARRAY

    # # ########################################################################################
