from time import time
from numpy.random import random_sample

from tango import DevState
from tango.server import Device, attribute, command
from tango.server import class_property, device_property

class BUK_M(Device):
	DEVICE_CLASS_DESCRIPTION = "блок управления и коммутации БУК-М"

# ########################################################################################
	status = attribute(
		label="status",
		dtype=str,
		doc="Статусное слово"
	)
	@status.read
	def status_read(self):
		status_bits = "110101011010110" # TODO

		response_str = ""

		if status_bits[0]:
			response_str = "Инициализация контроллера"
		if status_bits[1]:
			response_str = "Загружен файл конфигурации"
		if status_bits[2]:
			response_str = "Настройка оборудования"
		if status_bits[3]:
			response_str = "Все системы инициализированы"
		if status_bits[4]:
			response_str = "Циклограмма загружается"
		if status_bits[5]:
			response_str = "Циклограмма получена и обработана"
		if status_bits[6]:
			response_str = "Циклограмма выполняется"
		if status_bits[15]:
			response_str = "Запись команд запрещена"

		return response_str
# ########################################################################################
	@command(doc_in="???#TODO")
	def stop(self):
		pass # TODO
# ########################################################################################
	@command
	def get_cyclogram(self):
		pass # TODO
# ########################################################################################
	@command
	def cancel_cyclogram(self):
		pass # TODO
# ########################################################################################
	@command
	def reset_initialization(self):
		pass # TODO
# ########################################################################################
	@command
	def acknowledge_error(self):
		pass # TODO
# ########################################################################################
	@command
	def acknowledge_accident(self):
		pass # TODO
# ########################################################################################
	@command
	def reset_initialization_incomplete(self):
		pass # TODO
# ########################################################################################
	@command
	def enable_pulse_mode(self):
		pass # TODO
# ########################################################################################
	@command
	def disable_pulse_mode(self):
		pass # TODO

# ########################################################################################
	errors = attribute(
		label="errors",
		dtype=str,
		doc="Слово ошибок"
	)
	@errors.read
	def errors_read(self):
		errors_bits = "110101011010110" # TODO

		response_str = ""

		if errors_bits[0]: #TODO
			response_str = "TFTP-сервер недоступен"
		if errors_bits[1]:
			response_str = "Ошибка открытия файла конфигурации"
		if errors_bits[2]:
			response_str = "Ошибка загрузки файла конфигурации"
		if errors_bits[3]:
			response_str = "Ошибка при инициализации модулей или устройств"
		if errors_bits[4]:
			response_str = "Ошибка установки соединения"
		if errors_bits[5]:
			response_str = "Ошибка загрузки циклограммы"
		if errors_bits[6]:
			response_str = "Ошибка обработки циклограммы"
		if errors_bits[7]:
			response_str = "Ошибка при выполнении циклограммы"
		if errors_bits[8]:
			response_str = "Ошибка"
		if errors_bits[9]:
			response_str = "Потеря связи с сервером"
		if errors_bits[10]:
			response_str = "Авария модуля"
		if errors_bits[11]:
			response_str = "Неверная команда"
		if errors_bits[12]:
			response_str = "Авария"
		if errors_bits[13]:
			response_str = "Ошибка IRIG"

		return response_str






class BUK_M1(BUK_M):

	DEVICE_CLASS_DESCRIPTION = "БУК-М1"

	host = device_property(dtype=str)
	port = class_property(dtype=int, default_value=502)
	modbus_id = device_property(dtype=int)

# ########################################################################################
	status = attribute(
		label="status",
		dtype=str,
		doc="Статус источника тока"
	)
	@status.read
	def status_read(self):
		bit_0 = 1 # TODO
		bit_1 = 1 # TODO

		response_str = ""

		if ~bit_1 and ~bit_0:
			response_str = "отключен"
		if ~bit_1 and bit_0:
			response_str = "штатная работа"
		if bit_1 and ~bit_0:
			response_str = "останов в безопасном режиме"
		if bit_1 and bit_0:
			response_str = "режим прямого управления ШИМ"
		
		bit_2 = 1 # TODO

		if bit_2:
			response_str += ", инициализирован"
		else:
			response_str += ", неинициализирован"
# ########################################################################################
	error_warning = attribute(
		label="error_warning",
		dtype=str,
		doc="Значение кода ошибки/предупреждения"
	)
	@error_warning.read
	def error_warning_read(self):
		return 1 # TODO
# ########################################################################################
	output_current_float = attribute(
		label="output_current_float",
		dtype=float,
		doc="Значение выходного тока (float)"
	)
	@output_current_float.read
	def output_current_float_read(self):
		return 1 # TODO
# ########################################################################################
	load_current_float = attribute(
		label="load_current_float",
		dtype=float,
		doc="Значение тока в нагрузке (float)"
	)
	@load_current_float.read
	def load_current_float_read(self):
		return 1 # TODO
# ########################################################################################
	load_voltage_float = attribute(
		label="load_voltage_float",
		dtype=float,
		doc="Значение напряжения в нагрузке (float)"
	)
	@load_voltage_float.read
	def load_voltage_float_read(self):
		return 1 # TODO
# ########################################################################################
	temp_modulator_transistors_float = attribute(
		label="temp_modulator_transistors_float",
		dtype=float,
		doc="Значение температуры транзисторов модулятора (float)"
	)
	@temp_modulator_transistors_float.read
	def temp_modulator_transistors_float_read(self):
		return 1 # TODO
# ########################################################################################
	temp_throttle_float = attribute(
		label="temp_throttle_float",
		dtype=float,
		doc="Значение температуры дросселя (float)"
	)
	@temp_throttle_float.read
	def temp_throttle_float_read(self):
		return 1 # TODO
# ########################################################################################
	setpoint_output_current_float = attribute(
		label="setpoint_output_current_float",
		dtype=float,
		doc="Значение уставки выходного тока (float)"
	)
	@setpoint_output_current_float.read
	def setpoint_output_current_float_read(self):
		return 1 # TODO
# ########################################################################################
# ########################################################################################













if __name__ == "__main__":
	PowerSupply.run_server()