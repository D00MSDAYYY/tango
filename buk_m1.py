from buk_m import BUK_M
from collections import deque

from tango.server import  attribute, AttrWriteType

class BUK_M1(BUK_M):
# ########################################################################################
	_REGISTER_STATUS_WORD = 300001
	_REGISTER_ERROR_WARNING = 300002
	_REGISTER_OUTPUT_CURRENT_FLOAT = 300003
	_REGISTER_LOAD_CURRENT_FLOAT = 300005
	_REGISTER_LOAD_VOLTAGE_FLOAT = 300007
	_REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT = 300009
	_REGISTER_INDUCTOR_FLOAT = 300011
	_REGISTER_SETPOINT_CURRENT_FLOAT = 300013

	_MAX_PACKETS_BUFFER_SIZE = 1000

	_CURRENT_SUPPLIERS_NUMBER = 8
# ########################################################################################
	DEVICE_CLASS_DESCRIPTION = "БУК-М1. Источники тока корректоров"

	_packet_buffer = deque(maxlen=_MAX_PACKETS_BUFFER_SIZE)
# ########################################################################################
	def init_device(self):
		print('-> BUK_M1')
		
		super().init_device()

		print('status_read ==',self.status_read())
		print('error_warning_read == ',self.error_warning_read())
		print('output_current_float_read == ',self.output_current_float_read())
		print('load_current_float_read == ',self.load_current_float_read())
		print('load_voltage_float_read == ', self.load_voltage_float_read())
		print('temp_modulator_transistors_float_read == ', self.temp_modulator_transistors_float_read())
		print('temp_inductor_float_read == ', self.temp_inductor_float_read())
		print('setpoint_output_current_float_read == ', self.setpoint_output_current_float_read())

		print('<- BUK_M1')
		# self.error_warning_read()
		# self.enable_pulse_mode()
		# self.disable_pulse_mode()
# ########################################################################################
	def initialize_dynamic_attributes(self):

		def _supplier_status_read_FACTORY(index):
			def supplier_status_read() -> str:
				result = self._read_input_registers(self._REGISTER_STATUS_WORD, 1, index)

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
			
			return supplier_status_read

# ########################################################################################
		def _error_warning_read_FACTORY(index):
			def error_warning_read():
				result = self._read_input_registers(self._REGISTER_ERROR_WARNING, 1, index)

				if result is None:
					return "Ошибка чтения статуса источника"
				
				status_bits = format(result[0], '016b')[::-1]
				print(f"Ошибки\предупреждения источника: {status_bits}") # TODO

			return error_warning_read

# ########################################################################################

		def _output_current_float_read_FACTORY(index):
			def output_current_float_read():
				return self._read_float_from_input_register(self._REGISTER_OUTPUT_CURRENT_FLOAT, index)
			
			return output_current_float_read
	
# ########################################################################################

		def _load_current_float_read_FACTORY(index):
			def load_current_float_read():
				return self._read_float_from_input_register(self._REGISTER_LOAD_CURRENT_FLOAT, index)
			
			return load_current_float_read
	
# ########################################################################################

		def _load_voltage_float_read_FACTORY(index):
			def load_voltage_float_read():
				return self._read_float_from_input_register(self._REGISTER_LOAD_VOLTAGE_FLOAT, index)
			
			return load_voltage_float_read
	
# ########################################################################################

		def _temp_modulator_transistors_float_read_FACTORY(index):
			def temp_modulator_transistors_float_read():
				return self._read_float_from_input_register(self._REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT, index)
			
			return temp_modulator_transistors_float_read
	
# ########################################################################################

		def _temp_inductor_float_read_FACTORY(index):
			def temp_inductor_float_read():
				return self._read_float_from_input_register(self._REGISTER_INDUCTOR_FLOAT, index)
			
			return temp_inductor_float_read
	
# ########################################################################################

		def _setpoint_output_current_float_read_FACTORY(index):
			def setpoint_output_current_float_read():
				return self._read_float_from_input_register(self._REGISTER_SETPOINT_CURRENT_FLOAT, index)
			return setpoint_output_current_float_read

		for i in range(self._CURRENT_SUPPLIERS_NUMBER):
			status_attr = attribute(
				name=f"status_{i}",
				dtype=str,
				access=AttrWriteType.READ,
				fget=_supplier_status_read_FACTORY(i),  # Передаем метод чтения
				doc=f"Статус источника тока #{i}"
			)
			self.add_attribute(status_attr)

			error_warning_attr = attribute(
				name=f"error_warning_{i}",
				dtype=str,
				access=AttrWriteType.READ,
				fget=_error_warning_read_FACTORY(i),  # Передаем метод чтения
				doc=f"Значение кода ошибки/предупреждения #{i}"
			)
			self.add_attribute(error_warning_attr)

			output_current_float_attr = attribute(
				name=f"output_current_float_{i}",
				dtype=float,
				access=AttrWriteType.READ,
				fget=_output_current_float_read_FACTORY(i),  # Передаем метод чтения
				doc=f"Значение выходного тока #{i}"
			)
			self.add_attribute(output_current_float_attr)
			
			load_current_float_attr = attribute(
				name=f"load_current_float_{i}",
				dtype=float,
				access=AttrWriteType.READ,
				fget=_load_current_float_read_FACTORY(i),  # Передаем метод чтения
				doc=f"Значение тока в нагрузке #{i}"
			)
			self.add_attribute(load_current_float_attr)

			load_voltage_float_attr = attribute(
				name=f"load_voltage_float_{i}",
				dtype=float,
				access=AttrWriteType.READ,
				fget=_load_voltage_float_read_FACTORY(i),  # Передаем метод чтения
				doc=f"Значение напряжения в нагрузке #{i}"
			)
			self.add_attribute(load_voltage_float_attr)

			temp_modulator_transistors_float_attr = attribute(
				name=f"temp_modulator_transistors_float_{i}",
				dtype=float,
				access=AttrWriteType.READ,
				fget=_temp_modulator_transistors_float_read_FACTORY(i),  # Передаем метод чтения
				doc=f"Значение температуры транзисторов модулятора #{i}"
			)
			self.add_attribute(temp_modulator_transistors_float_attr)

			temp_inductor_float_attr = attribute(
				name=f"temp_inductor_float_{i}",
				dtype=float,
				access=AttrWriteType.READ,
				fget=_temp_inductor_float_read_FACTORY(i),  # Передаем метод чтения
				doc=f"Значение температуры дросселя #{i}"
			)
			self.add_attribute(temp_inductor_float_attr)

			setpoint_output_current_float_attr = attribute(
				name=f"setpoint_output_current_float_{i}",
				dtype=float,
				access=AttrWriteType.READ,
				fget=_setpoint_output_current_float_read_FACTORY(i),  # Передаем метод чтения
				doc=f"Значение уставки выходного тока #{i}"
			)
			self.add_attribute(setpoint_output_current_float_attr)

# ########################################################################################
	def _process_pulse_mode_packet(self, data: bytes, addr: tuple):
		"""Обработка Pulse пакета"""
		import struct

		try:
			expected_size = (4	#	cостояние, тип числа int32
			+ 4 				#	счетчик пакетов, тип числа int32
			+ 8 				#	время отправки пакета в секундах с начала «эпохи», тип числа double
			+ (8 * 8) 			#	массив из 8ми чисел с показаниями токов, тип числа double
			+ (8 * 8)) 			#	массив из 8ми чисел с показаниями напряжений, тип числа double

			if len(data) != expected_size:
				raise ValueError(f"Неверный размер пакета: {len(data)} байт, ожидается {expected_size} байт")

			fmt = '>2i d 16d'	# 2 int32 + 1 double + 16 double
			unpacked_data = struct.unpack(fmt, data)

			currents = unpacked_data[3:(3 + self._CURRENT_SUPPLIERS_NUMBER)]   # 8 значений токов
			voltages = unpacked_data[11:(11 + self._CURRENT_SUPPLIERS_NUMBER)]  # 8 значений напряжений

			decoded_data = {
				'state': unpacked_data[0],
				'packet_counter': unpacked_data[1],
				'timestamp': unpacked_data[2],
				'currents': list(currents),
				'voltages': list(voltages)
			}
			print('decoded data: ', decoded_data)

			self._packet_buffer.append(decoded_data)

			for i, (current, voltage) in enumerate(zip(currents, voltages)):
				self.push_change_event(f"load_current_float_{i}", current)
				self.push_change_event(f"load_voltage_float_{i}", voltage)

		except Exception as e:
			print(f"Ошибка обработки Pulse пакета БУК-М1 : {e}")