from time import time
from numpy.random import random_sample

from tango import DevState
from tango.server import Device, attribute, command
from tango.server import class_property, device_property


class BUK_M1(Device):

	DEVICE_CLASS_DESCRIPTION = "BUK_M1 low voltage source"

	host = device_property(dtype=str)
	port = class

	def init_device(self):
		super().init_device()
		self.info_stream(f"Power supply connection details: {self.host}:{self.port}")
		self.set_state(DevState.ON)
		self.set_status("Power supply is ON")

	current = attribute(
		label="Current",
		dtype=float,
		unit="A",
		format="8.4f",
		doc="the power supply current"
	)

	@current.read
	def current_read(self):
		return self._current
	
	@command
	def test_command1(self):
		self.info_stream("Test command is activated")

	@command(dtype_in=int, doc_in="send 1 to receive a test string", dtype_out=str)
	def test_command2(self, num:int) -> str:
		if num == 1:
			return "this is a test string"
		else :
			return ""

if __name__ == "__main__":
	PowerSupply.run_server()