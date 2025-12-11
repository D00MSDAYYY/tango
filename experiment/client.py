import tango

# create a device object
proxy = tango.DeviceProxy("test/power_supply/1")

# you can ping it
# print(f"Ping: {proxy.ping()}")

# every device has a state and status which can be checked with:
# proxy.enable_pulse_mode = False
# print("load_current_float = ", proxy.load_current_float)
# proxy.subscribe_event("pulse_mode_values", tango.EventType.PERIODIC_EVENT, lambda data : print(data))

attrs = proxy.get_attribute_list()
print(f"\nДоступные атрибуты: {attrs}", sep="\n")
