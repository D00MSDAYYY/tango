from buk_m import BUK_M
from tango.server import device_property

class power_supply(BUK_M):

# ########################################################################################

	_REGISTER_STATUS_WORD 						= 300001
	_REGISTER_ERROR_WARNING 					= 300002
	_REGISTER_OUTPUT_CURRENT_FLOAT 				= 300003
	_REGISTER_LOAD_CURRENT_FLOAT 				= 300005
	_REGISTER_LOAD_VOLTAGE_FLOAT 				= 300007
	_REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT 	= 300009
	_REGISTER_INDUCTOR_FLOAT 					= 300011
	_REGISTER_SETPOINT_CURRENT_FLOAT 			= 300013

# ########################################################################################

	DEVICE_CLASS_DESCRIPTION 	= "Отдельный класс под каждый источник тока"
	modbus_id 					= device_property(dtype=int)
	name 						= device_property(dtype=int) # удобное имя источника 

	def init_device(self):
		super().init_device()

	def supplier_status_read(self) -> str:
		result = self._read_input_registers(self._REGISTER_STATUS_WORD, 1, self.modbus_id)

		if result is None:
			return "Ошибка чтения статуса источника"

		status_bits = format(result[0], '016b')[::-1]

		print(f"Статус источника: {status_bits} из регистра {self._REGISTER_STATUS_WORD}")

		state_map = {
			(0, 0): "отключен",
			(1, 0): "штатная работа", 
			(0, 1): "останов в безопасном режиме",
			(1, 1): "режим прямого управления ШИМ"
		}

		state_key = (int(status_bits[1]), int(status_bits[0]))
		
		response_str = state_map.get(state_key, "неизвестное состояние")

		if int(status_bits[2]):
			response_str += ", инициализирован"
		else:
			response_str += ", неинициализирован"

		return response_str
	
	def error_warning_read(self):
		result = self._read_input_registers(self._REGISTER_ERROR_WARNING, 1, self.modbus_id)

		if result is None:
			return "Ошибка чтения статуса источника"
		
		status_bits = format(result[0], '016b')[::-1]
		print(f"Ошибки\предупреждения источника: {status_bits}") # TODO
			
	def output_current_float_read(self):
		return self._read_float_from_input_register(self._REGISTER_OUTPUT_CURRENT_FLOAT, self.modbus_id)
	
	def load_current_float_read(self):
		return self._read_float_from_input_register(self._REGISTER_LOAD_CURRENT_FLOAT, self.modbus_id)
			
	def load_voltage_float_read(self):
		return self._read_float_from_input_register(self._REGISTER_LOAD_VOLTAGE_FLOAT, self.modbus_id)
	
	def temp_modulator_transistors_float_read(self):
		return self._read_float_from_input_register(self._REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT, self.modbus_id)
	
	def temp_inductor_float_read(self):
		return self._read_float_from_input_register(self._REGISTER_INDUCTOR_FLOAT, self.modbus_id)
	
	def setpoint_output_current_float_read(self):
		return self._read_float_from_input_register(self._REGISTER_SETPOINT_CURRENT_FLOAT, self.modbus_id)
			