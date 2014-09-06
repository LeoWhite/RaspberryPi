import smbus
import time

# Select the bus to use.. This will be 0 for revision 1 boards
bus = smbus.SMBus(1)


# BrightPi's i2c address
address = 0x70

visibleLEDs=[1,3,4,6]
IRLEDs=[0,2,5,7]

# Select the visible LEDs and set to 50% brightness (Range 0-50)
ActiveLEDs=0
for x in visibleLEDs:
  bus.write_byte_data(address, x + 1, 25)
  ActiveLEDs |= (1 << x)

# And turn them on
bus.write_byte_data(address, 0x00, ActiveLEDs)

# Wait 5 seconds
time.sleep(5)

# Now switch over to the IR LEDs
ActiveLEDs = 0
for x in IRLEDs:
  bus.write_byte_data(address, x + 1, 25)
  ActiveLEDs |= (1 << x)

# And turn them on
bus.write_byte_data(address, 0x00, ActiveLEDs)

# Wait another 5 seconds
time.sleep(5)

# Turn off all the LEDS
bus.write_byte_data(address, 0x00, 0x00)

