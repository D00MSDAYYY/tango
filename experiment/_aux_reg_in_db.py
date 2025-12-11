from tango import Database
import tango

dev_info = tango.DbDevInfo()
dev_info.server = "server/test"
dev_info._class = "power_supply"
dev_info.name = "test/power_supply/1"

db = tango.Database()

properties = {
    'host': ['10.10.9.72'],
    'port': ['502'],
    'modbus_id': 1
}
db.add_device(dev_info)

db.put_device_property(dev_info.name, properties)
