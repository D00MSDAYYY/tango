from tango import DevState
from tango.server import Device
from tango.server import class_property, device_property

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse

class _TANGO_MODBUS(Device):
# ########################################################################################
	_OFFSET_INPUT_REGISTER = 300001
	_OFFSET_HOLDING_REGISTER = 400001

# ########################################################################################
	DEVICE_CLASS_DESCRIPTION = "вспомогательный класс для взаимодействия между Tango Controls и ModbusTCP"
	host = device_property(dtype=str)
	port = class_property(dtype=int, default_value=502)
	modbus_id = device_property(dtype=int)

# ########################################################################################
	def init_device(self):
		print('начало инициализации _TANGO_MODBUS')
		super().init_device()
		self.connect_to_modbus()
		print('конец инициализации _TANGO_MODBUS')

# ########################################################################################
	def connect_to_modbus(self):
		'''Инициализация Modbus клиента'''
		self.modbus_client = ModbusTcpClient(
			host=self.host,
			port=self.port,
			timeout=2.0,
			retries=3
		)

		is_connected = False
		try:
			is_connected =  self.modbus_client.connect()

			if is_connected:
				self.set_state(DevState.ON)
				print(f"Успешное подключение к {self.host}:{self.port}")
			else:
				self.set_state(DevState.FAULT)
				print(f"Не удалось подключиться к {self.host}:{self.port}")
		
		except Exception as e:
			print(f"Исключение в connect_to_modbus : {e}")

# ########################################################################################
	def _read_input_registers(self, address, count=1):
		'''Чтение input registers (3xxxx)'''

		try:
			modbus_address = address - self._OFFSET_INPUT_REGISTER

			response = self.modbus_client.read_input_registers(
				address=modbus_address, 
				count=count,
				device_id=self.modbus_id
			)
			return self._process_response(response)
		
		except Exception as e:
			print(f"Выброшено исключение: {e}")
			return None

# ########################################################################################
	def _read_holding_registers(self, address, count, unit=0):
		'''Чтение holding registers (4xxxx)'''

		try:
			modbus_address = address - self._OFFSET_HOLDING_REGISTER

			response = self.modbus_client.read_holding_registers(
				address=modbus_address,  
				count=count,
				device_id=self.modbus_id
			)
			return self._process_response(response)
		
		except Exception as e:
			print(f"Выброшено исключение: {e}")
			return None

# ########################################################################################
	def _process_response(self, response):
		'''Обработка ответа Modbus'''

		if response.isError():
			print(f"Modbus ошибка в ответе: {response}")
			return None
		
		elif isinstance(response, ExceptionResponse):
			print(f"Modbus исключение: {response}")
			return None
		
		else:
			if hasattr(response, 'registers'):
				return response.registers
			else:
				return None
