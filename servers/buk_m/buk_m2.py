from buk_m import BUK_M
from collections import deque

from tango.server import attribute


class BUK_M2(BUK_M):

    # ########################################################################################

    _REGISTER_STATUS_WORD = 300001
    _REGISTER_ERROR_WARNING = 300002
    _REGISTER_OUTPUT_CURRENT_FLOAT = 300003
    _REGISTER_LOAD_CURRENT_FLOAT = 300005
    _REGISTER_LOAD_VOLTAGE_FLOAT = 300007
    _REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT = 300009
    _REGISTER_INDUCTOR_FLOAT = 300011


    _MAX_PACKETS_BUFFER_SIZE = 1000

# ########################################################################################

    DEVICE_CLASS_DESCRIPTION = "БУК-М1. Источники тока корректоров"

    _packet_buffer = deque(maxlen=_MAX_PACKETS_BUFFER_SIZE)

# ########################################################################################

    def init_device(self):
        super().init_device()

# ########################################################################################

    def _process_pulse_mode_packet(self, data: bytes, addr: tuple):  # TODO
        """Обработка Pulse пакета"""

# ########################################################################################

    error_warning = attribute(
        label="error_warning",
        dtype=str,
        doc="Значение кода ошибки/предупреждения"
    )

    @error_warning.read
    def _(self, index):
        pass

# ########################################################################################

    output_current_float = attribute(
        label="output_current_float",
        dtype=float,
        doc="Значение выходного тока (float)"
    )

    @output_current_float.read
    def _(self, index):
        return self._read_float32_from_input_register(self._REGISTER_OUTPUT_CURRENT_FLOAT, index)

# ########################################################################################

    load_current_float = attribute(
        label="load_current_float",
        dtype=float,
        doc="Значение тока в нагрузке (float)"
    )

    @load_current_float.read
    def _(self, index):
        return self._read_float32_from_input_register(self._REGISTER_LOAD_CURRENT_FLOAT, index)

# ########################################################################################

    load_voltage_float = attribute(
        label="load_voltage_float",
        dtype=float,
        doc="Значение напряжения в нагрузке (float)"
    )

    @load_voltage_float.read
    def _(self, index):
        return self._read_float32_from_input_register(self._REGISTER_LOAD_VOLTAGE_FLOAT, index)

# ########################################################################################

    temp_modulator_transistors_float = attribute(
        label="temp_modulator_transistors_float",
        dtype=float,
        doc="Значение температуры транзисторов модулятора (float)"
    )

    @temp_modulator_transistors_float.read
    def _(self, index):
        return self._read_float32_from_input_register(self._REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT, index)

# ########################################################################################

    temp_inductor_float = attribute(
        label="temp_inductor_float",
        dtype=float,
        doc="Значение температуры дросселя (float)"
    )

    @temp_inductor_float.read
    def _(self, index):
        return self._read_float32_from_input_register(self._REGISTER_INDUCTOR_FLOAT, index)

# ########################################################################################

    setpoint_output_current_float = attribute(
        label="setpoint_output_current_float",
        dtype=float,
        doc="Значение уставки выходного тока (float)"
    )

    @setpoint_output_current_float.read
    def _(self, index):
        return self._read_float32_from_input_register(self._REGISTER_SETPOINT_CURRENT_FLOAT, index)
