import 

# address 7-bit I2C address to read from
# data    pointer to the buffer where the data is to be stored
# count   number of bytes to read from I2C and store in the buffer
# returns 0 on success, error code otherwise
i2c_address = 0

def i2c_read(address, data, count):
    if i2c_address != address:

        i2c_address = address
