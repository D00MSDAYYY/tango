from buk_m1 import BUK_M1
from tango.server import device_property, attribute, AttrWriteType


class power_supply(BUK_M1):

    # ########################################################################################

    _REGISTER_STATUS_WORD = 300001
    _REGISTER_ERROR_WARNING = 300002
    _REGISTER_OUTPUT_CURRENT_FLOAT = 300003
    _REGISTER_LOAD_CURRENT_FLOAT = 300005
    _REGISTER_LOAD_VOLTAGE_FLOAT = 300007
    _REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT = 300009
    _REGISTER_INDUCTOR_FLOAT = 300011
    _REGISTER_SETPOINT_CURRENT_FLOAT = 300013

# ########################################################################################

    DEVICE_CLASS_DESCRIPTION = "Отдельный класс под каждый источник тока"
    modbus_id = device_property(dtype=int)
    name = device_property(dtype=str)  # удобное имя для источника тока
# ########################################################################################

    def init_device(self):
        super().init_device()

# ########################################################################################

    def initialize_dynamic_attributes(self):
# fmt: off
        attribute_configs = [
                ('status', 							str, 	self._supplier_status_read_FACTORY, 				"Статус источника тока"),
                ('error_warning', 					str, 	self._error_warning_read_FACTORY, 					"Ошибки/предупреждения"),
                ('output_current_float', 			float, 	self._output_current_float_read_FACTORY, 			"Выходной ток"),
                ('load_current_float', 				float, 	self._load_current_float_read_FACTORY, 				"Ток в нагрузке"),
                ('load_voltage_float', 				float, 	self._load_voltage_float_read_FACTORY, 				"Напряжение в нагрузке"),
                ('temp_modulator_transistors_float',float, 	self._temp_modulator_transistors_float_read_FACTORY,"Температура транзисторов"),
                ('temp_inductor_float', 			float, 	self._temp_inductor_float_read_FACTORY, 			"Температура дросселя"),
                ('setpoint_output_current_float', 	float, 	self._setpoint_output_current_float_read_FACTORY, 	"Уставка выходного тока")
        ]
# fmt: on
        for attr_name, dtype, factory in attribute_configs:
            attr_obj = attribute(
                name=f"{attr_name}",
                dtype=dtype,
                access=AttrWriteType.READ,
                fget=factory(self.modbus_id)
            )
            self.add_attribute(attr_obj)
