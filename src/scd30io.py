import time
import smbus

class SCD30IO:

    DEVICE_ADDRESS = 0x61
    bus = None

    def __init__(self):
        self.bus = smbus.SMBus(1)

    # address 7-bit I2C address to read from
    # data    array of bytes
    # returns 0 on success, error code otherwise
    def i2c_read(self, data):
        count = len(data)
        data = bytearray(
                self.bus.read_i2c_block_data(self.DEVICE_ADDRESS, address, count))[0: count]


    # data must be an byte array
    def i2c_write(self, data):
        self.bus.write_block_data(self.DEVICE_ADDRESS, data[0], data[1:])

    def sleep_usec(self, useconds):
        time.sleep(useconds)
