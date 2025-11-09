from tango import DevState
from tango.server import Device
from tango.server import class_property, device_property

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse


class _BUK_MODBUS(Device):
	host = device_property(dtype=str)
	port = class_property(dtype=int, default_value=502)
	modbus_id = device_property(dtype=int)

	_OFFSET_INPUT_REGISTER = 300001
	_OFFSET_HOLDING_REGISTER = 400001

# ########################################################################################
	def init_device(self):
		super().init_device()
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
			modbus_address = address - self._OFFSET_INPUT_REGISTER
			response = self.modbus_client.read_input_registers(
				address=modbus_address,  # 0-based адрес
				count=count,
				device_id=self.modbus_id
			)
			return self._process_response(response)
		except ModbusException as e:
			print(f"Modbus ошибка чтения {address}: {e}")
			return None
		
		# except Exception as e:
		# 	print(f"Неизвестная ошибка: {e}")
		# 	return None
		
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
		
