from .. import buk_m
from buk_m import *


if __name__ == "__main__":
	buk_m.BUK_M1.host = "10.10.9.96"
	buk_m.BUK_M1.port = 502
	buk_m.BUK_M1.modbus_id = 0

	buk_m.BUK_M1.run_server()