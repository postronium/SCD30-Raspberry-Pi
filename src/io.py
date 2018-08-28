import time
import smbus

DEVICE_ADDRESS = 0x61
bus = None

def i2c_init():
    sub = smbus.SMBus(1)

# address 7-bit I2C address to read from
# data    pointer to the buffer where the data is to be stored
# count   number of bytes to read from I2C and store in the buffer
# returns 0 on success, error code otherwise
def i2c_read(address, data, count):
    data = bytearray(
            bus.read_i2c_block_data(DEVICE_ADDRESS, address, count))[0: count]


# data must be an byte array
def i2c_write(address, data, count):
    bus.write_block_data(DEVICE_ADDRESS, address, data)

def sleep_usec(useconds):
    time.sleep(useconds)
