from buk_m import BUK_M
from buk_m1 import BUK_M1
from buk_m2 import BUK_M2

if __name__ == "__main__":
	BUK_M1.host = "10.10.9.96"
	BUK_M1.port = 502
	BUK_M1.modbus_id = 0

	BUK_M1.run_server()