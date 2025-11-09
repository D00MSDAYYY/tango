import threading
import socket 

from _buk_modbus import _BUK_MODBUS
from tango.server import class_property, command, attribute
from abc import abstractmethod

class BUK_M(_BUK_MODBUS): 
	pulse_udp_port =  class_property(dtype=int, default_value=4000)
	_udp_socket = None

	_is_listening : bool
	_listener_thread : threading.Thread

# ########################################################################################
	_REGISTER_STATUS_WORD = 300001
	_REGISTER_ERROR_WORD = 300002
	_REGISTER_ACCIDENT_WORD = 300003
	_REGISTER_COMMAND_WORD = 400001
	_REGISTER_COMMAND_PULSE = 400002

# ########################################################################################
	DEVICE_CLASS_DESCRIPTION = "блок управления и коммутации БУК-М"

	_inner_watchdog_thread : threading.Timer # периодически посылает запросы по модбас
	_outer_watch_dog : threading.Timer # периодически проверяет, давно ли клиенты просили присылать данные (если давно, то отписывает)

# ########################################################################################
	def init_device(self):
		super().init_device()

# ########################################################################################
	# status = attribute( #TODO
	# 	label="status",
	# 	dtype=str,
	# 	doc="Статусное слово"
	# )
	# @status.getter 
	def status_read(self):
		result = self._read_input_registers(self._REGISTER_STATUS_WORD, 1)

		if result is None:
			return "Ошибка чтения слова статуса"
		
		status_bits = format(result[0], '016b')[::-1]
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
	def _do_command(self, addr,  command_code ):
		self.modbus_client.write_register(
				address= addr - self._OFFSET_HOLDING_REGISTER,
				value=command_code,
				device_id=self.modbus_id
			)
	
	_BIN_CODE_STOP = 1 << 1
	_BIN_CODE_GET_CYCLOGRAMM = 1 << 2
	_BIN_CODE_CANCEL_CYCLOGRAMM = 1 << 3
	_BIN_CODE_RESET_INITIALIZATION = 1 << 5
	_BIN_CODE_ACKNOWLEDGE_ERROR = 1 << 6
	_BIN_CODE_ACKNOWLEDGE_ACCIDENT = 1 << 7
	_BIN_CODE_RESET_INITIALIZATION_INCOMPLETE = 1 << 13

	@command(doc_in="???#TODO")
	def stop(self):
		return self._do_command(self._BIN_CODE_STOP)
		
# ########################################################################################
	@command
	def get_cyclogram(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_GET_CYCLOGRAMM)
	
# ########################################################################################
	@command
	def cancel_cyclogram(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_CANCEL_CYCLOGRAMM)
	
# ########################################################################################
	@command
	def reset_initialization(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_RESET_INITIALIZATION)
	
# ########################################################################################
	@command
	def acknowledge_error(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_ACKNOWLEDGE_ERROR)
	
# ########################################################################################
	@command
	def acknowledge_accident(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_ACKNOWLEDGE_ACCIDENT)
	
# ########################################################################################
	@command
	def reset_initialization_incomplete(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._BIN_CODE_RESET_INITIALIZATION_INCOMPLETE)
	
# ########################################################################################

	_CODE_ENABLE_PULSE_MODE = 1
	_CODE_DISABLE_PULSE_MODE = 2
	_INNER_WATCHDOG_INTERVAL_SEC = 30
	_OUTER_WATCHDOG_INTERVAL_SEC = 100

	@abstractmethod
	def _process_pulse_packet(self, data: bytes, addr: tuple):
		pass

	def _udp_listener(self):
		print('in listener')
		self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._udp_socket.settimeout(1.0)
		
		try:
			self._udp_socket.bind((self.port, self.pulse_udp_port))  # Порт для Pulse режима
			
			while self._is_listening:
				try:
					data, addr = self._udp_socket.recvfrom(1024)
					self._process_pulse_packet(data, addr)
				except socket.timeout:
					continue
				except Exception as e:
					self.error_stream(f"Ошибка UDP: {e}")
					
		except Exception as e:
			self.error_stream(f"Ошибка UDP socket: {e}")
		finally:
			if self._udp_socket:
				self._udp_socket.close()

	@command
	def enable_pulse_mode(self):
		self._do_command(self._REGISTER_COMMAND_PULSE, self._CODE_ENABLE_PULSE_MODE)

		
		if hasattr(self, '_inner_watchdog_thread') and self._inner_watchdog_thread:
			self._inner_watchdog_thread.cancel()

		self._inner_watchdog_thread = threading.Timer(interval=self._INNER_WATCHDOG_INTERVAL_SEC,
												function= self.enable_pulse_mode )
		self._inner_watchdog_thread.daemon = True
		self._inner_watchdog_thread.start()

		self._is_listening = True
		self._listener_thread = threading.Thread(daemon=True, target=self._udp_listener)
		self._listener_thread.start()
		self.info_stream(f"UDP listener для Pulse mode запущен на порту {self.pulse_udp_port}")
	
# ########################################################################################
	@command
	def disable_pulse_mode(self):
		self._inner_watchdog_thread = None
		if hasattr(self, '_inner_watchdog_thread') and self._inner_watchdog_thread:
			self._inner_watchdog_thread.cancel()
			self._inner_watchdog_thread = None

		self._is_listening = False
		self._listener_thread.cancel()
		self._udp_socket.close()

		return self._do_command(self._REGISTER_COMMAND_PULSE, self._CODE_DISABLE_PULSE_MODE)

# ########################################################################################
	errors = attribute(
		label="errors",
		dtype=str,
		doc="Слово ошибок"
	)
	@errors.read
	def errors_read(self):
		result = self._read_input_registers(self._REGISTER_ERROR_WORD, 1)

		if result is None:
			return "Ошибка чтения слова ошибок"

		errors_bits = format(result[0], '016b')[::-1]
		print(f"Слово ошибок: {errors_bits}")

		errors_map = {
			0: "TFTP-сервер недоступен",
			1: "Ошибка открытия файла конфигурации",
			2: "Ошибка загрузки файла конфигурации",
			3: "Ошибка при инициализации модулей или устройств",
			4: "Ошибка установки соединения",
			5: "Ошибка загрузки циклограммы", 
			6: "Ошибка обработки циклограммы",
			7: "Ошибка при выполнении циклограммы",
			8: "Ошибка",
			9: "Потеря связи с сервером",
			10: "Авария модуля",
			11: "Неверная команда",
			12: "Авария",
			13: "Ошибка IRIG"
		}

		active_errors = []
		for bit_index, message in errors_map.items():
			if errors_bits[bit_index] == '1':
				active_errors.append(message)

		return "; ".join(active_errors) if active_errors else "Ошибок нет"

	# ########################################################################################
	accidents = attribute(
		label="accidents",
		dtype=str,
		doc="Слово аварий"
	)
	@accidents.read
	def _(self):
		return "функция слова аварий пока не поддерживается"

