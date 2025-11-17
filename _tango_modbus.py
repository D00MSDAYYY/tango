from tango import DevState
from tango.server import Device
from tango.server import class_property, device_property

from pymodbus.client import ModbusTcpClient
from pymodbus.pdu import ExceptionResponse

import struct

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
		print('-> _TANGO_MODBUS')

		super().init_device()
		self.connect_to_modbus()
		
		print('<- _TANGO_MODBUS')

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
	def _read_input_registers(self, address, count, device_id): #TODO
		'''Чтение input registers (3xxxx)'''

		try:
			modbus_address = address - self._OFFSET_INPUT_REGISTER

			response = self.modbus_client.read_input_registers(
				address=modbus_address, 
				count=count,
				device_id=device_id
			)
			return self._process_response(response)
		
		except Exception as e:
			print(f"Выброшено исключение: {e}")
			return None

# ########################################################################################
	def _read_holding_registers(self, address, count, device_id):
		'''Чтение holding registers (4xxxx)'''

		try:
			modbus_address = address - self._OFFSET_HOLDING_REGISTER

			response = self.modbus_client.read_holding_registers(
				address=modbus_address,  
				count=count,
				device_id=device_id
			)
			return self._process_response(response)
		
		except Exception as e:
			print(f"Выброшено исключение: {e}")
			return None

# ########################################################################################
	def _process_response(self, response): # TODO return tuple 
		'''Обработка ответа Modbus'''

		if response.isError():

			error_messages = {
			1: "Недопустимый код функции",
			2: "Недопустимый адрес данных", 
			3: "Недопустимое значение данных",
			4: "Ошибка устройства",
			5: "Подтверждение",
			6: "Устройство занято"
		}
			message = error_messages.get(response.exception_code, "Неизвестная ошибка")
			print('Ошибка в ответе Modbus : ', message)

			return None
		
		else:
			if hasattr(response, 'registers'):
				return response.registers
			else:
				return None
			
# ########################################################################################
	def _read_float_from_input_register(self,  addr, device_id):
		result = self._read_input_registers(addr, 2, device_id)

		if result is None:
			print(f"Не удалось прочитать регистр {addr}")
			return None

		try:
			data_bytes = struct.pack('>2H', result[0], result[1])
			value = struct.unpack('>f', data_bytes)[0]

			print(f"Значение (float) : {value}")

			return float(value)

		except Exception as e:
			self.error_stream(f"Ошибка преобразования данных (float): {e}")
			return None

# ########################################################################################
	def _read_double_from_input_register(self, addr, device_id):
		result = self._read_input_registers(addr, 4, device_id)

		if result is None:
			print(f"Не удалось прочитать регистры начиная с {addr}")
			return None

		try:
			data_bytes = struct.pack('>4H', result[0], result[1], result[2], result[3])
			value = struct.unpack('>d', data_bytes)[0]

			print(f"Прочитано double значение из регистра {addr}: {value}")

			return float(value)

		except Exception  as e:
			self.error_stream(f"Ошибка преобразования данных в double: {e}")
			return None