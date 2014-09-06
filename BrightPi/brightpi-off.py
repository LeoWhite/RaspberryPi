import smbus
import time
bus = smbus.SMBus(1)
address = 0x70

#def write(value):
#        bus.write_byte_data(address, 0x0f, value)
#        return -1

#results = bus.read_i2c_block_data(address, 0x0f, 24)
#print results

#bus.write_i2c_block_data(address, 0x0f, default_setup)

status = bus.read_byte_data(address, 0x00)
print status
bus.write_byte_data(address, 0x00, 0x00)

status = bus.read_byte_data(address, 0x00)
print status
#results = bus.read_i2c_block_data(address, 0x0f, 24)
#print results
