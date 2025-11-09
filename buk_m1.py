from buk_m import BUK_M
from collections import deque

from tango.server import  attribute

class BUK_M1(BUK_M):
# ########################################################################################
	_REGISTER_STATUS_WORD = 300001
	_REGISTER_ERROR_WARNING = 300002
	# _REGISTER_OUTPUT_CURRENT_FLOAT = 
	# _REGISTER_ = 
	# _REGISTER_ = 
	# _REGISTER_ = 
	# _REGISTER_ = 
	_MAX_PACKETS_BUFFER_SIZE = 1000

# ########################################################################################
	DEVICE_CLASS_DESCRIPTION = "БУК-М1. Источники тока корректоров"

	_packet_buffer = deque(maxlen=_MAX_PACKETS_BUFFER_SIZE)
# ########################################################################################
	def init_device(self):
		super().init_device()
		self.status_read()
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
	def status_read(self):
		result = self._read_input_registers(self._REGISTER_STATUS_WORD, 1)

		if result is None:
			return "Ошибка чтения статуса источника"

		status_bits = format(result[0], '016b')[::-1]

		print(f"Статус источника: {status_bits}")

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
	def _process_pulse_packet(self, data: bytes, addr: tuple):
		"""Обработка Pulse пакета"""
		import struct

		try:
			expected_size = (4	#	cостояние, тип числа int32;
			+ 4 				#	счетчик пакетов, тип числа int32;
			+ 8 				#	время отправки пакета в секундах с начала «эпохи», тип числа double;
			+ (8 * 8) 			#	массив из 8ми чисел с показаниями токов, тип числа double;
			+ (8 * 8)) 			#	массив из 8ми чисел с показаниями напряжений, тип числа double;

			if len(data) != expected_size:
				raise ValueError(f"Неверный размер пакета: {len(data)} байт, ожидается {expected_size} байт")
			
			# Распаковываем данные (big-endian, так как Modbus TCP использует сетевой порядок)
			# 2 int32 + 1 double + 16 double
			fmt = '>2i d 16d'
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
	def error_warning_read(self):
		result = self._read_input_registers(self._REGISTER_ERROR_WARNING, 1)

		if result is None:
			return "Ошибка чтения статуса источника"
		
		status_bits = format(result[0], '016b')[::-1]
		print(f"Ошибки\предупреждения источника: {status_bits}") # TODO
	
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
