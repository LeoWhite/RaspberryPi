import smbus
import time
bus = smbus.SMBus(0)
address = 0x07

#def write(value):
#        bus.write_byte_data(address, 0x0f, value)
#        return -1

results = bus.read_i2c_block_data(address, 0x0f, 24)
print results

default_setup = [  # 0x0f, # Start bytes 
6, # Frquency
                    0, 0, 1, # Left motor
                    0, 0, 1, # Right motor
                    0, 0, # Servo 0
                    0, 0, # Servo 1
                    0, 0, # Servo 2
                    0, 0, # Servo 3
                    0, 0, # Servo 4
                    0, 0, # Servo 6
                    50, # Accelerometer
                    0, 0, # Impact
                    0x02, 0x26, # Low battery
                    0x07, # I2C address 
                    0]    # Clock frequency
print default_setup                   
bus.write_i2c_block_data(address, 0x0f, default_setup)

results = bus.read_i2c_block_data(address, 0x0f, 24)
print results
