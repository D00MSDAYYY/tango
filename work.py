from time import time
from numpy.random import random_sample

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
	DEVICE_CLASS_DESCRIPTION = "блок управления и коммутации БУК-М"

	_REGISTER_STATUS_WORD = 300001
	_REGISTER_ERROR_WORD = 300002
	_REGISTER_ACCIDENT_WORD = 300003
	_REGISTER_COMMAND_WORD = 400001
	_REGISTER_COMMAND_PULSE = 400002

	def init_device(self):
		super().init_device()

		print("=== ТЕСТ status.getter ===")

		print(self.status_read())


# ########################################################################################
	# status = attribute(
	# 	label="status",
	# 	dtype=str,
	# 	doc="Статусное слово"
	# )
	# @status.getter 
	def status_read(self):
		result = self._read_input_registers(300001, 1)

		if result is None:
			return "Ошибка чтения статуса"
		
		status_bits = format(result[0], '016b')
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
	def _do_command(self, command_code ):
		response = self.modbus_client.write_register(
				address=self._REGISTER_COMMAND_WORD - self._OFFSET_HOLDING_REGISTER,
				value=command_code,
				device_id=self.modbus_id
			)
		return self._process_response(response)
	
	_AUX_16_ZEROS_LIST = ['0'] * 16

	_BIN_LIST_STOP = 	_AUX_16_ZEROS_LIST.copy() 	
	_BIN_LIST_STOP[1]	= '1'

	_BIN_LIST_GET_CYCLOGRAMM = _AUX_16_ZEROS_LIST.copy() 	
	_BIN_LIST_GET_CYCLOGRAMM[2] = '1'

	_BIN_LIST_CANCEL_CYCLOGRAMM = _AUX_16_ZEROS_LIST.copy() 		
	_BIN_LIST_CANCEL_CYCLOGRAMM[3] = '1'				

	_BIN_LIST_RESET_INITIALIZATION = 	_AUX_16_ZEROS_LIST.copy() 	
	_BIN_LIST_RESET_INITIALIZATION[5] = '1'

	_BIN_LIST_ACKNOWLEDGE_ERROR = _AUX_16_ZEROS_LIST.copy() 	
	_BIN_LIST_ACKNOWLEDGE_ERROR[6] = '1'
						   
	_BIN_LIST_ACKNOWLEDGE_ACCIDENT = 	_AUX_16_ZEROS_LIST.copy() 	
	_BIN_LIST_ACKNOWLEDGE_ACCIDENT[7] = '1'

	_BIN_LIST_RESET_INITIALIZATION_INCOMPLETE = _AUX_16_ZEROS_LIST.copy() 	
	_BIN_LIST_RESET_INITIALIZATION_INCOMPLETE[13] = '1'

	def _bin_list_to_int(bin_list):
		return int(''.join(bin_list), 2)


	@command(doc_in="???#TODO")
	def stop(self):
		return self._do_command(self._bin_list_to_int(self._BIN_LIST_STOP))
		
# ########################################################################################
	@command
	def get_cyclogram(self):
		return self._do_command(self._bin_list_to_int(self._BIN_LIST_GET_CYCLOGRAMM))
	
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





if __name__ == "__main__":
	BUK_M.host = "10.10.9.89"
	BUK_M.port = 502
	BUK_M.modbus_id = 0

	BUK_M.run_server()





