import threading
import socket 

from _tango_modbus import _TANGO_MODBUS
from tango.server import class_property, command, attribute
from abc import abstractmethod

class BUK_M(_TANGO_MODBUS): 
# ########################################################################################
	_REGISTER_STATUS_WORD = 300001 # TODO Final const
	_REGISTER_ERROR_WORD = 300002
	_REGISTER_ACCIDENT_WORD = 300003
	_REGISTER_COMMAND_WORD = 400001
	_REGISTER_PULSE_MODE = 400002

	_CODE_STOP = 1 << 1
	_CODE_GET_CYCLOGRAMM = 1 << 2
	_CODE_CANCEL_CYCLOGRAMM = 1 << 3
	_CODE_RESET_INITIALIZATION = 1 << 5
	_CODE_ACKNOWLEDGE_ERROR = 1 << 6
	_CODE_ACKNOWLEDGE_ACCIDENT = 1 << 7
	_CODE_RESET_INITIALIZATION_INCOMPLETE = 1 << 13

	_CODE_PULSE_MODE_ENABLE = 1
	_CODE_PULSE_MODE_DISABLE = 2
	_PULSE_MODE_INNER_WATCHDOG_INTERVAL_SEC = 30
	_PULSE_MODE_OUTER_WATCHDOG_INTERVAL_SEC = 100

# ########################################################################################
	DEVICE_CLASS_DESCRIPTION = "блок управления и коммутации БУК-М"
	pulse_udp_port =  class_property(dtype=int, default_value=4000)
	MODBUS_ID_PARENT_BUK_M = class_property(dtype=int, default_value=0) # адрес Modbus_ID корневого устройства 

	_udp_socket : socket.socket
	_is_listening : bool = False
	_udp_listener_thread : threading.Thread
	_udp_listener_lock = threading.Lock()

# ########################################################################################
	def init_device(self):
		print('-> BUK_M')

		super().init_device()

		print('Статус БУК-М : ',self.status_read())
		print('Ошибки : ', self.errors_read())

		print('<- BUK_M')

# ########################################################################################
	# m1_status = attribute( #TODO
	# 	label="status",
	# 	dtype=str,
	# 	doc="Статус устройства"
	# )
	# @status.getter 
	def buk_m_status_read(self):
		result = self._read_input_registers(self._REGISTER_STATUS_WORD, 1, self.MODBUS_ID_PARENT_BUK_M)

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

		status = "Статус не определен"
		for bit_index, message in status_map.items():
			if int(status_bits[bit_index]):
				status = message
		
		return status
	

# ########################################################################################
	def _do_command(self, comm_addr,  command_code, device_id):
		self.modbus_client.write_register(
				address= comm_addr - self._OFFSET_HOLDING_REGISTER,
				value=command_code,
				device_id=device_id
			)

	@command(doc_in="#TODO")
	def stop(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_STOP, self.MODBUS_ID_PARENT_BUK_M)
		
# ########################################################################################
	@command
	def get_cyclogram(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_GET_CYCLOGRAMM, self.MODBUS_ID_PARENT_BUK_M)
	
# ########################################################################################
	@command
	def cancel_cyclogram(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_CANCEL_CYCLOGRAMM, self.MODBUS_ID_PARENT_BUK_M)
	
# ########################################################################################
	@command
	def reset_initialization(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_RESET_INITIALIZATION, self.MODBUS_ID_PARENT_BUK_M)
	
# ########################################################################################
	@command
	def acknowledge_error(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_ACKNOWLEDGE_ERROR, self.MODBUS_ID_PARENT_BUK_M)
	
# ########################################################################################
	@command
	def acknowledge_accident(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_ACKNOWLEDGE_ACCIDENT, self.MODBUS_ID_PARENT_BUK_M)
	
# ########################################################################################
	@command
	def reset_initialization_incomplete(self):
		return self._do_command(self._REGISTER_COMMAND_WORD, self._CODE_RESET_INITIALIZATION_INCOMPLETE, self.MODBUS_ID_PARENT_BUK_M)
	
# ########################################################################################
	@abstractmethod
	def _process_pulse_mode_packet(self, data: bytes, addr: tuple):
		pass

# ########################################################################################
	def _udp_listener(self):
		self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._udp_socket.settimeout(1.0)
		
		try:
			self._udp_socket.bind((self.host, self.pulse_udp_port))
			
			while self._is_listening:
				try:
					data, addr = self._udp_socket.recvfrom(1024)
					self._process_pulse_mode_packet(data, addr)

				except socket.timeout:
					continue

		except Exception as e:
			if self._is_listening:
				print(f"Исключение в _udp_listener : {e}")

		finally:
			try:
				self._udp_socket.shutdown()
				self._udp_socket.close()
				print(f"_udp_socket {self.host}:{self.port} закрыт")
			except:
				pass

# ########################################################################################
	def _start_udp_listener(self):
		"""Запуск UDP listener в отдельном потоке"""
		with self._udp_listener_lock:
			if self._is_listening and self._udp_listener_thread.is_alive():
				print("_udp_listener_thread уже запущен")
				return
				
			self._is_listening = True
			self._udp_listener_thread = threading.Thread(target=self._udp_listener, daemon=True)
			self._udp_listener_thread.start()

		print("_udp_listener_thread запущен")

# ########################################################################################
	def _stop_udp_listener(self):
		'''Остановка UDP listener'''
		with self._listener_lock:
			self._is_listening = False

			if self._udp_listener_thread.is_alive():
				self._udp_listener_thread.join(timeout=2.0)
				print("_udp_listener_thread остановлен")

# ########################################################################################
	@command
	def enable_pulse_mode(self):
		self._do_command(self._REGISTER_PULSE_MODE, self._PULSE_MODE_CODE_ENABLE, self.MODBUS_ID_PARENT_BUK_M)
		self._start_udp_listener()

		print(f"Pulse mode включен. UDP listener на порту {self.pulse_udp_port}")


# ########################################################################################
	@command
	def disable_pulse_mode(self):
		self._do_command(self._REGISTER_PULSE_MODE, self._CODE_DISABLE_PULSE_MODE, self.MODBUS_ID_PARENT_BUK_M)
		self._stop_udp_listener()

		print(f"Pulse mode выключен на порту {self.pulse_udp_port}")

# ########################################################################################
	# errors = attribute(
	# 	label="errors",
	# 	dtype=str,
	# 	doc="Слово ошибок"
	# )
	# @errors.read
	def buk_m_errors_read(self):
		result = self._read_input_registers(self._REGISTER_ERROR_WORD, 1, self.MODBUS_ID_PARENT_BUK_M)

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

