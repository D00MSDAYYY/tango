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
	def _read_input_registers(self, address, count=1, unit=None):
		"""Чтение input registers (3xxxx)"""
		if unit is None:
			unit = self.modbus_id
			
		try:
			# ПРЕОБРАЗОВАНИЕ 1-based -> 0-based
			# Документация: 300001, 300002, 300003...
			# pymodbus:       0,      1,      2...
			modbus_address = address - 300001
			
			response = self.modbus_client.read_input_registers(
				address=modbus_address,  # 0-based адрес
				count=count,
				device_id=unit
			)
			return self._process_response(response)
		except ModbusException as e:
			self.error_stream(f"Modbus ошибка чтения {address}: {e}")
			return None
		
# ########################################################################################
	def _read_holding_registers(self, address, count, unit=0):
		"""Чтение holding registers (4xxxx)"""
		try:
			response = self.client.read_holding_registers(
				address=address - 400001,  # pymodbus использует 0-based
				count=count,
				slave=unit
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

	def init_device(self):
		super().init_device()
		self.set_state(DevState.INIT)
		self.connect_to_modbus()

		print("testing")
		status_word = self._read_input_registers(300001,1)[0]
		binary_str = format(status_word, '016b') 
		print(binary_str)
# ########################################################################################
	status = attribute(
		label="status",
		dtype=str,
		doc="Статусное слово"
	)
	@status.read
	def _(self):
		status_bits = format(self._read_input_registers(300001,1)[0], '016b') 

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
	def _(self):
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
	_BUK_M.host = "10.10.9.89"
	_BUK_M.port = 502
	_BUK_M.modbus_id = 0

	_BUK_M.run_server()





