


# ########################################################################################
# ########################################################################################


class BUK_M1_CORRECTOR_CURRENT_SUPPLIER(BUK_M): # ModbusID 1-8

	DEVICE_CLASS_DESCRIPTION = "Источники тока корректоров"

# ########################################################################################
	status = attribute(
		label="status",
		dtype=str,
		doc="Статус источника тока"
	)
	@status.read
	def _(self):
		bit_0 = 1 # TODO
		bit_1 = 1 # TODO

		response_str = ""

		if ~bit_1 and ~bit_0:
			response_str = "отключен"
		if ~bit_1 and bit_0:
			response_str = "штатная работа"
		if bit_1 and ~bit_0:
			response_str = "останов в безопасном режиме"
		if bit_1 and bit_0:
			response_str = "режим прямого управления ШИМ"
		
		bit_2 = 1 # TODO

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
# ########################################################################################
# #####

class BUK_M1_M2_IO(Device): # ModbusID 17
	error_warning = attribute(
		label="error_warning",
		dtype=str,
		doc="Значение кода ошибки/предупреждения"
	)
	@error_warning.read
	def _(self):
		return 1 # TODO
# ########################################################################################
	inputs_status = attribute(
		label="inputs_status",
		dtype=str,
		doc="Состояние входов"
	)
	@inputs_status.read
	def _(self):
		return 1 # TODO
# ########################################################################################
	outputs_status = attribute(
		label="outputs_status",
		dtype=str,
		doc="Состояние выходов"
	)
	@outputs_status.read
	def _(self):
		return 1 # TODO
# ########################################################################################
# ########################################################################################



class BUK_M2_HIGH_FREQUENCY(Device): # ModbusID 1
	DEVICE_CLASS_DESCRIPTION = "Высокоточные АЦП-ЦАП (БУК-М2)"

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
	normalized_ADC1_readings = attribute(
		label="normalized_ADC1_readings",
		dtype=float,
		doc="Нормированные показания АЦП 1"
	)
	@normalized_ADC1_readings.read
	def _(self):
		return 1 # TODO
	
# ########################################################################################
	normalized_ADC2_readings = attribute(
		label="normalized_ADC2_readings",
		dtype=float,
		doc="Нормированные показания АЦП 2"
	)
	@normalized_ADC2_readings.read
	def _(self):
		return 1 # TODO

# ########################################################################################
	normalized_ADC3_readings = attribute(
		label="normalized_ADC3_readings",
		dtype=float,
		doc="Нормированные показания АЦП 3"
	)
	@normalized_ADC3_readings.read
	def _(self):
		return 1 # TODO

# ########################################################################################
	normalized_value_DAC_setting = attribute(
		label="normalized_value_DAC_setting",
		dtype=float,
		doc="Нормированное значение текущей уставки ЦАП"
	)
	@normalized_value_DAC_setting.read
	def _(self):
		return 1 # TODO
	
# ########################################################################################
	temp_ADC_board = attribute(
		label="temp_ADC_board",
		dtype=float,
		doc="Значение температуры платы АЦП"
	)
	@temp_ADC_board.read
	def _(self):
		return 1 # TODO

