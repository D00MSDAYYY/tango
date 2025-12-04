from tango import Database
import tango

dev_info = tango.DbDevInfo()
dev_info.server = "serv_buk_m1/test"
dev_info._class = "BUK_M1"
dev_info.name = "test/BUK_M1/2"

db = tango.Database()

properties = {
    'host': ['10.10.9.76'],
    'port': ['502']
}
db.add_device(dev_info)

db.put_device_property(dev_info.name, properties)


