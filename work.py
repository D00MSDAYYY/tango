import threading
import time

from tango import DevState
from tango.server import Device, attribute, command
from tango.server import class_property, device_property

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse

class _BUK_M(Device):
	host = device_property(dtype=str)
	port = class_property(dtype=int, default_value=502)
	modbus_id = device_property(dtype=int)

	_OFFSET_INPUT_REGISTER = 300001
	_OFFSET_HOLDING_REGISTER = 400001

# ########################################################################################
	def init_device(self):
		super().init_device()
		self.set_state(DevState.INIT)
		self.connect_to_modbus()

# ########################################################################################
	def connect_to_modbus(self):
		# Инициализация Modbus клиента
		self.modbus_client = ModbusTcpClient(
			host=self.host,
			port=self.port,
			timeout=2.0,
			retries=3
		)
		# Подключение к Modbus устройству
		is_connected = False
		try:
			is_connected =  self.modbus_client.connect()
		except Exception as e:
			self.error_stream(f"Ошибка Modbus подключения: {e}")

		# Попытка подключения
		if is_connected:
			self.set_state(DevState.ON)
			self.info_stream(f"Успешное подключение к {self.host}:{self.port}")
		else:
			self.set_state(DevState.FAULT)
			self.error_stream(f"Ошибка подключения к {self.host}:{self.port}")

# ########################################################################################
	def _read_input_registers(self, address, count=1):
		"""Чтение input registers (3xxxx)"""

		try:
			# ПРЕОБРАЗОВАНИЕ 1-based -> 0-based
			# Документация: 300001, 300002, 300003...
			# pymodbus:       0,      1,      2...
			modbus_address = address - self._OFFSET_INPUT_REGISTER
			
			response = self.modbus_client.read_input_registers(
				address=modbus_address,  # 0-based адрес
				count=count,
				device_id=self.modbus_id
			)
			return self._process_response(response)
		except ModbusException as e:
			self.error_stream(f"Modbus ошибка чтения {address}: {e}")
			return None
		
# ########################################################################################
	def _read_holding_registers(self, address, count, unit=0):
		"""Чтение holding registers (4xxxx)"""
		try:
			modbus_address = address - self._OFFSET_HOLDING_REGISTER

			response = self.modbus_client.read_holding_registers(
				address=modbus_address,  # pymodbus использует 0-based
				count=count,
				device_id=self.modbus_id
			)
			return self._process_response(response)
		except ModbusException as e:
			print(f"Modbus ошибка: {e}")
			return None

# ########################################################################################
	def _process_response(self, response):
		"""Обработка ответа Modbus"""

		if response.isError():
			self.error_stream(f"Modbus ошибка в ответе: {response}")
			return None
		elif isinstance(response, ExceptionResponse):
			self.error_stream(f"Modbus exception: {response}")
			return None
		else:
			return response.registers if hasattr(response, 'registers') else None
		

# ########################################################################################
# ########################################################################################
class BUK_M(_BUK_M): # ModbusID 0
	_REGISTER_STATUS_WORD = 300001
	_REGISTER_ERROR_WORD = 300002
	_REGISTER_ACCIDENT_WORD = 300003
	_REGISTER_COMMAND_WORD = 400001
	_REGISTER_COMMAND_PULSE = 400002

# ########################################################################################
	DEVICE_CLASS_DESCRIPTION = "блок управления и коммутации БУК-М"

	class WatchDog:
		interval : int 
		callback = None
		
		def __init__(self, interval, callback):
			self.interval = interval
			self.callback = callback

			self._timer = threading.Timer(self.interval, self.callback)

	_inner_watch_dog : WatchDog # периодически посылает запросы по модбас
	_outer_watch_dog : WatchDog # периодически проверяет, давно ли клиенты просили присылать данные (если давно, то отписывает)

# ########################################################################################
	def init_device(self):
		super().init_device()

# ########################################################################################
	# status = attribute( #TODO
	# 	label="status",
	# 	dtype=str,
	# 	doc="Статусное слово"
	# )
	# @status.getter 
	def status_read(self):
		result = self._read_input_registers(self._REGISTER_STATUS_WORD, 1)

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

		for bit_index, message in status_map.items():
			if status_bits[bit_index] == '1':
				return message
		
		return "Статус не определен"
	

# ########################################################################################
	def _do_command(self, addr,  command_code ):
		response = self.modbus_client.write_register(
				address= addr - self._OFFSET_HOLDING_REGISTER,
				value=command_code,
				device_id=self.modbus_id
			)
		return self._process_response(response)
	
	_BIN_CODE_STOP = 1 << 1
	_BIN_CODE_GET_CYCLOGRAMM = 1 << 2
	_BIN_CODE_CANCEL_CYCLOGRAMM = 1 << 3
	_BIN_CODE_RESET_INITIALIZATION = 1 << 5
	_BIN_CODE_ACKNOWLEDGE_ERROR = 1 << 6
	_BIN_CODE_ACKNOWLEDGE_ACCIDENT = 1 << 7
	_BIN_CODE_RESET_INITIALIZATION_INCOMPLETE = 1 << 13

	@command(doc_in="???#TODO")
	def stop(self):
		return self._do_command(self._BIN_CODE_STOP)
		
# ########################################################################################
	@command
	def get_cyclogram(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_GET_CYCLOGRAMM)
	
# ########################################################################################
	@command
	def cancel_cyclogram(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_CANCEL_CYCLOGRAMM)
	
# ########################################################################################
	@command
	def reset_initialization(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_RESET_INITIALIZATION)
	
# ########################################################################################
	@command
	def acknowledge_error(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_ACKNOWLEDGE_ERROR)
	
# ########################################################################################
	@command
	def acknowledge_accident(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_ACKNOWLEDGE_ACCIDENT)
	
# ########################################################################################
	@command
	def reset_initialization_incomplete(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_RESET_INITIALIZATION_INCOMPLETE)
	
# ########################################################################################

	_CODE_ENABLE_PULSE_MODE = 1
	_CODE_DISABLE_PULSE_MODE = 2

	@command
	def enable_pulse_mode(self):
		is_success = self._do_command(self._REGISTER_COMMAND_PULSE, self._CODE_ENABLE_PULSE_MODE)

		if is_success and not self._inner_watch_dog :
			self._inner_watch_dog = self.WatchDog(interval=30, callback=lambda: ( self.enable_pulse_mode() ))
		return is_success
	
# ########################################################################################
	@command
	def disable_pulse_mode(self):
		return self._do_command(self._REGISTER_COMMAND_PULSE, self._CODE_DISABLE_PULSE_MODE)

# ########################################################################################
	errors = attribute(
		label="errors",
		dtype=str,
		doc="Слово ошибок"
	)
	@errors.read
	def errors_read(self):
		result = self._read_input_registers(self._REGISTER_ERROR_WORD, 1)

		if result is None:
			return "Ошибка чтения слова ошибок"

		errors_bits = format(result[0], '016b')[::-1]
		print(f"Слово ошибок: {errors_bits}")

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
	def _(self):
		return "функция слова аварий пока не поддерживается"


# ########################################################################################
# ########################################################################################


class BUK_M1_CORRECTOR_CURRENT_SUPPLIER(BUK_M): # ModbusID 1-8
	_REGISTER_STATUS_WORD = 300001
	_REGISTER_ERROR_WARNING = 300002
	# _REGISTER_OUTPUT_CURRENT_FLOAT = 
	# _REGISTER_ = 
	# _REGISTER_ = 
	# _REGISTER_ = 
	# _REGISTER_ = 

# ########################################################################################
	DEVICE_CLASS_DESCRIPTION = "Источники тока корректоров"

# ########################################################################################
	def init_device(self):
		super().init_device()
		print(self.status_read())
# ########################################################################################
	# status = attribute(
	# 	label="status",
	# 	dtype=str,
	# 	doc="Статус источника тока"
	# )
	# @status.read
	def status_read(self):
		result = self._read_input_registers(300001, 1)

		if result is None:
			return "Ошибка чтения статуса источника"

		status_bits = format(result[0], '016b')[::-1]
		print(f"Статус источника: {status_bits}")

		# Состояния по битам 0 и 1
		state_map = {
			(0, 0): "отключен",
			(1, 0): "штатная работа", 
			(0, 1): "останов в безопасном режиме",
			(1, 1): "режим прямого управления ШИМ"
		}

		# Определяем основное состояние
		bit_0 = 1 if status_bits[0] == '1' else 0  # Бит 0 (младший)
		bit_1 = 1 if status_bits[1] == '1' else 0  # Бит 1
		state_key = (bit_1, bit_0)
		
		response_str = state_map.get(state_key, "неизвестное состояние")

		# Добавляем статус инициализации (бит 2)
		bit_2 = status_bits[2] == '1'  

		if bit_2:
			response_str += ", инициализирован"
		else:
			response_str += ", неинициализирован"

		return response_str
	
# ########################################################################################
	error_warning = attribute(
		label="error_warning",
		dtype=str,
		doc="Значение кода ошибки/предупреждения"
	)
	@error_warning.read
	def _(self):
		return 1 # TODO
	
# ########################################################################################
	output_current_float = attribute(
		label="output_current_float",
		dtype=float,
		doc="Значение выходного тока (float)"
	)
	@output_current_float.read
	def _(self):
		return 1 # TODO
# ########################################################################################
	load_current_float = attribute(
		label="load_current_float",
		dtype=float,
		doc="Значение тока в нагрузке (float)"
	)
	@load_current_float.read
	def _(self):
		return 1 # TODO
# ########################################################################################
	load_voltage_float = attribute(
		label="load_voltage_float",
		dtype=float,
		doc="Значение напряжения в нагрузке (float)"
	)
	@load_voltage_float.read
	def _(self):
		return 1 # TODO
# ########################################################################################
	temp_modulator_transistors_float = attribute(
		label="temp_modulator_transistors_float",
		dtype=float,
		doc="Значение температуры транзисторов модулятора (float)"
	)
	@temp_modulator_transistors_float.read
	def _(self):
		return 1 # TODO
# ########################################################################################
	temp_throttle_float = attribute(
		label="temp_throttle_float",
		dtype=float,
		doc="Значение температуры дросселя (float)"
	)
	@temp_throttle_float.read
	def _(self):
		return 1 # TODO
# ########################################################################################
	setpoint_output_current_float = attribute(
		label="setpoint_output_current_float",
		dtype=float,
		doc="Значение уставки выходного тока (float)"
	)
	@setpoint_output_current_float.read
	def _(self):
		return 1 # TODO


if __name__ == "__main__":
	BUK_M1_CORRECTOR_CURRENT_SUPPLIER.host = "10.10.9.89"
	BUK_M1_CORRECTOR_CURRENT_SUPPLIER.port = 502
	BUK_M1_CORRECTOR_CURRENT_SUPPLIER.modbus_id = 0

	BUK_M1_CORRECTOR_CURRENT_SUPPLIER.run_server()





