import time
import smbus

class SCD30IO:

    DEVICE_ADDRESS = 0x61
    bus = None

    STATUS_FAIL = 1
    STATUS_OK = 0

    def __init__(self):
        self.bus = smbus.SMBus(1)
        print("SCD30IO Init")

    # address 7-bit I2C address to read from
    # data    array of bytes
    # returns 0 on success, error code otherwise
    def i2c_read(self, data, size):
        data = bytearray(
                self.bus.read_i2c_block_data(self.DEVICE_ADDRESS, 0, size))[0: size]
        print("SCD30IO Read " + str(size) + " bytes from device " + str(self.DEVICE_ADDRESS))
        print("SCD30IO Recived Data : ")
        for byte in data:
            print(byte)
        return self.STATUS_OK


    # data must be an byte array
    def i2c_write(self, data):
        self.bus.write_block_data(self.DEVICE_ADDRESS, data[0], data[1:])
        print("SCD30IO Write Data to " + str(self.DEVICE_ADDRESS) + " : " + str(data))
        return self.STATUS_OK

    def sleep_usec(self, useconds):
        time.sleep(useconds)
        print("SCD30IO Sleep " + str(useconds) + "us")
        return self.STATUS_OK
