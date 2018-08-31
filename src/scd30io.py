import time
import smbus

class SCD30IO:

    DEVICE_ADDRESS = 0x61
    bus = None

    STATUS_FAIL = 1
    STATUS_OK = 0

    # WORKS!
    def __init__(self):
        self.bus = smbus.SMBus(3)
        #print("SCD30IO Init")

    # TESTE ADN WORKS!
    # returns array of bytes
    def i2c_read(self, size):
        data = bytearray(
                self.bus.read_i2c_block_data(self.DEVICE_ADDRESS, 0))
        #print("SCD30IO Read " + str(size) + " bytes from device " + str(self.DEVICE_ADDRESS))
        #print("SCD30IO Recived Data : ")
        #for byte in data:
        #    print(byte)
        return data


    # TESTE ADN WORKS!
    # data must be an byte array
    def i2c_write(self, data):
        self.bus.write_i2c_block_data(self.DEVICE_ADDRESS, data[0], data[1:])
        #print("SCD30IO Write Data to " + str(self.DEVICE_ADDRESS) + " : " + str(data))

    # NOT TESTED
    def sleep_usec(self, useconds):
        time.sleep(useconds)
        #print("SCD30IO Sleep " + str(useconds) + "us")

    # TESTE ADN WORKS!
    def get_configured_address(self):
        return self.DEVICE_ADDRESS
