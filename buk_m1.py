from buk_m import BUK_M
from collections import deque

from tango.server import  attribute

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
	# status = attribute(
	# 	label="status",
	# 	dtype=str,
	# 	doc="Статус источника тока"
	# )
	# @status.read
	def status_read(self, index):
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
			state = unpacked_data[0]
			packet_counter = unpacked_data[1]
			timestamp = unpacked_data[2]

			currents = unpacked_data[3:11]   # 8 значений токов
			voltages = unpacked_data[11:19]  # 8 значений напряжений

			decoded_data = {
				'state': state,
				'packet_counter': packet_counter,
				'timestamp': timestamp,
				'currents': list(currents),
				'voltages': list(voltages)
			}
			print('decoded data: ', decoded_data)

			self._packet_buffer.append(decoded_data)

		except Exception as e:
			print(f"Ошибка обработки Pulse пакета БУК-М1 : {e}")
	
# ########################################################################################
	# error_warning = attribute(
	# 	label="error_warning",
	# 	dtype=str,
	# 	doc="Значение кода ошибки/предупреждения"
	# 	)
	# @error_warning.read
	def error_warning_read(self, index):
		result = self._read_input_registers(self._REGISTER_ERROR_WARNING, 1, index)

		if result is None:
			return "Ошибка чтения статуса источника"
		
		status_bits = format(result[0], '016b')[::-1]
		print(f"Ошибки\предупреждения источника: {status_bits}") # TODO

# ########################################################################################
	# output_current_float = attribute(
	# 	label="output_current_float",
	# 	dtype=float,
	# 	doc="Значение выходного тока (float)"
	# )
	# @output_current_float.read
	def output_current_float_read(self, index):
		return self._read_float_from_input_register(self._REGISTER_OUTPUT_CURRENT_FLOAT, index)
	
# ########################################################################################
	# load_current_float = attribute(
	# 	label="load_current_float",
	# 	dtype=float,
	# 	doc="Значение тока в нагрузке (float)"
	# )
	# @load_current_float.read
	def load_current_float_read(self, index):
		return self._read_float_from_input_register(self._REGISTER_LOAD_CURRENT_FLOAT, index)
	
# ########################################################################################
	# load_voltage_float = attribute(
	# 	label="load_voltage_float",
	# 	dtype=float,
	# 	doc="Значение напряжения в нагрузке (float)"
	# )
	# @load_voltage_float.read
	def load_voltage_float_read(self, index):
		return self._read_float_from_input_register(self._REGISTER_LOAD_VOLTAGE_FLOAT, index)
	
# ########################################################################################
	# temp_modulator_transistors_float = attribute(
	# 	label="temp_modulator_transistors_float",
	# 	dtype=float,
	# 	doc="Значение температуры транзисторов модулятора (float)"
	# )
	# @temp_modulator_transistors_float.read
	def temp_modulator_transistors_float_read(self, index):
		return self._read_float_from_input_register(self._REGISTER_TEMP_MODULATOR_TRANSISTORS_FLOAT, index)
	
# ########################################################################################
	# temp_inductor_float = attribute(
	# 	label="temp_inductor_float",
	# 	dtype=float,
	# 	doc="Значение температуры дросселя (float)"
	# )
	# @temp_inductor_float.read
	def temp_inductor_float_read(self, index):
		return self._read_float_from_input_register(self._REGISTER_INDUCTOR_FLOAT, index)
	
# ########################################################################################
	# setpoint_output_current_float = attribute(
	# 	label="setpoint_output_current_float",
	# 	dtype=float,
	# 	doc="Значение уставки выходного тока (float)"
	# )
	# @setpoint_output_current_float.read
	def setpoint_output_current_float_read(self, index):
		return self._read_float_from_input_register(self._REGISTER_SETPOINT_CURRENT_FLOAT, index)
