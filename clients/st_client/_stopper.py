import tango as tc


tango_db = tc.Database("127.0.0.1", "11000")

proxy = tc.DeviceProxy("tango://127.0.0.1:11000/" + "sys/database/2")
proxy.stop_poll_attribute("Timing_minimum")
