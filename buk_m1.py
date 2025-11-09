from buk_m import BUK_M

from tango.server import  attribute

class BUK_M1(BUK_M): # ModbusID 1-8
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
	def _process_pulse_packet(self, data: bytes, addr: tuple):
		"""Обработка Pulse пакета"""
		try:
			# Декодируем данные используя абстрактный метод
			decoded_data = self._pulse_mode_processor(data)
			
			# Сохраняем данные
			self._current_packet_data = decoded_data
			self._packet_count += 1
			
			# Логируем
			self._log_pulse_data(decoded_data)
			
			# Обновляем Tango атрибуты
			self._update_attributes(decoded_data)
			
		except Exception as e:
			self.error_stream(f"Ошибка обработки Pulse пакета: {e}")
	
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
		print(f"Ошибки\предупреждения источника: {status_bits}")
	
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
