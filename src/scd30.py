# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Not fully implemented yet
# They may be bugs even in the functions with the comment 'WOKRS!'

from scd30io import SCD30IO
import numpy

class SCD30:


    CMD_START_PERIODIC_MEASUREMENT = 0x0010
    CMD_STOP_PERIODIC_MEASUREMENT = 0x0104
    CMD_READ_MEASUREMENT = 0x0300
    CMD_GET_DATA_READY = 0x0202
    CMD_SET_MEASUREMENT_INTERVAL = 0x4600
    CMD_SET_TEMPERATURE_OFFSET = 0x5403
    CMD_SET_ALTITUDE = 0x5102

    WORD_LEN = 2
    COMMAND_LEN = 2
    MAX_BUFFER_WORDS = 24

    CRC8_POLYNOMIAL = 0x31
    CRC8_INIT = 0xFF
    CRC8_LEN = 1

    STATUS_FAIL = 1
    STATUS_OK = 0

    CO2_DATA_INDEX = 0
    TEMP_DATA_INDEX = 1
    HUMIDITY_DATA_INDEX = 2

    def __init__(self):
        self.io = SCD30IO()

    # data  : array of bytes
    # count : length of array
    # TESTE ADN WORKS!
    def generate_crc(self, data, count):
        crc = self.CRC8_INIT
        # calculates 8-Bit checksum with given polynomial
        for current_byte in xrange(count):
            crc ^= (data[current_byte]);
            for crc_bit in xrange(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ self.CRC8_POLYNOMIAL;
                else:
                    crc = (crc << 1);
                crc = crc%256
        return crc

    # TESTE ADN WORKS!
    def check_crc(self, data, count, checksum):
        if self.generate_crc(data, count) != checksum :
            return self.STATUS_FAIL
        return self.STATUS_OK


    # num_words : (unsigned integer 16 bit) number of data words to read (without CRC bytes)
    # return    : data (unsigned integer 16 bit)
    def i2c_read_bytes(self, num_words):
        size = num_words * (self.WORD_LEN + self.CRC8_LEN)
        word_buf = [0]*self.MAX_BUFFER_WORDS     #not sure about it
        buf8 = self.io.i2c_read(size)
        data = [0]*(num_words*self.WORD_LEN)

        # check the CRC for each word
        i = 0
        j = 0
        while(i < size):
            if self.check_crc(buf8[i:i+self.WORD_LEN], self.WORD_LEN, buf8[i + self.WORD_LEN]) == self.STATUS_FAIL:
                raise Exception("Fail on CRC Check, Data : " + str(buf8[i]) + ", " + str(buf8[i+1]) + " Recived Checksum: " + str(buf8[i + self.WORD_LEN]))

            data[j] = buf8[i]
            data[j + 1] = buf8[i + 1]

            i += self.WORD_LEN + self.CRC8_LEN
            j += self.WORD_LEN

        return data


    # cmd : (uint16)
    # args : Array of (uint16)
    # return the buffer with the command and the argments with their CRC
    def fill_cmd_send_buf(self, cmd, args):
        BUF_SIZE = self.COMMAND_LEN + (self.WORD_LEN + self.CRC8_LEN)*len(args);
        idx = 0
        buf = [0]*BUF_SIZE

        #store cmd in buffer
        buf[idx] = ((cmd & 0xFF00) >> 8) % 256
        idx += 1
        buf[idx] = ((cmd & 0x00FF) >> 0) % 256
        idx += 1

        for arg in args:
            #not sure about this (what does the function be16_to_cpu ?)
            #generate crc for the arg
            word = [0]*2
            word[0] = ((arg & 0xFF00) >> 8) % 256
            word[1] = ((arg & 0x00FF) >> 0) % 256
            crc = self.generate_crc(word, self.WORD_LEN)

            #store the arg with the crc in buffer
            buf[idx] = word[0]
            idx += 1
            buf[idx] = word[1]
            idx += 1
            buf[idx] = crc
            idx += 1

        return buf

    def fill_cmd_send_buf_no_crc(self, cmd, args):
        BUF_SIZE = self.COMMAND_LEN + self.WORD_LEN*len(args);
        idx = 0
        buf = [0]*BUF_SIZE

        #store cmd in buffer
        buf[idx] = ((cmd & 0xFF00) >> 8) % 256
        idx += 1
        buf[idx] = ((cmd & 0x00FF) >> 0) % 256
        idx += 1

        for arg in args:
            #not sure about this (what does the function be16_to_cpu ?)
            #generate crc for the arg
            word = [0]*2
            word[0] = ((arg & 0xFF00) >> 8) % 256
            word[1] = ((arg & 0x00FF) >> 0) % 256

            #store the arg with the crc in buffer
            buf[idx] = word[0]
            idx += 1
            buf[idx] = word[1]
            idx += 1

        return buf


    def i2c_write(self, command):
        buf = self.fill_cmd_send_buf(command, []);

        self.io.i2c_write(buf);


    # This function reads data words from the sensor after a command has been sent
    # cmd       : (16bit integer)
    # num_words : number of 16bit int arguments
    def i2c_read_bytes_from_cmd(self, cmd, num_words):
        self.i2c_write(cmd)

        return self.i2c_read_bytes(num_words)



    # TESTE ADN WORKS!
    # ambient_pressure_mbar : (u16 array)
    def start_periodic_measurement(self, ambient_pressure_mbar):
        BUF_SIZE = self.COMMAND_LEN + self.WORD_LEN + self.CRC8_LEN;

        if ambient_pressure_mbar and (
                ambient_pressure_mbar < 700 or
                ambient_pressure_mbar > 1400):
            # out of allowable range
            return self.STATUS_FAIL

        buf = self.fill_cmd_send_buf(self.CMD_START_PERIODIC_MEASUREMENT, [ambient_pressure_mbar])

        self.io.i2c_write(buf)

    # TESTE ADN WORKS!
    def stop_periodic_measurement(self):
        return self.i2c_write(self.CMD_STOP_PERIODIC_MEASUREMENT)


    # TESTE ADN WORKS!
    def read_measurement(self):
        bytes_buf = [0]*12 # 2 words for each co2, temperature, humidity
        word_buf = [0]*(len(bytes_buf)/2);
        data = [0]*(len(word_buf)/2)

        bytes_buf = self.i2c_read_bytes_from_cmd(self.CMD_READ_MEASUREMENT,
                len(bytes_buf) / self.WORD_LEN)


        for i in xrange(len(word_buf)):
            word_buf[i] = (bytes_buf[i*2] << 8) | bytes_buf[i*2+1]
            print(word_buf[i])

        #convert to int32
        data[self.CO2_DATA_INDEX] = (word_buf[0] << 16) | word_buf[1]
        data[self.TEMP_DATA_INDEX] = (word_buf[2] << 16) | word_buf[3]
        data[self.HUMIDITY_DATA_INDEX] = (word_buf[4] << 16) | word_buf[5]

        #Convert data to float32
        floatData = numpy.array(data, dtype=numpy.int32)
        return floatData.view('float32')


    # TESTE ADN WORKS!
    # interval : (u16 integer)
    def set_measurement_interval(self, interval_sec):
        BUF_SIZE = self.COMMAND_LEN + self.WORD_LEN + self.CRC8_LEN;

        if interval_sec < 2 or interval_sec > 1800:
            return self.STATUS_FAIL

        buf = self.fill_cmd_send_buf(self.CMD_SET_MEASUREMENT_INTERVAL, [interval_sec])
        self.io.i2c_write(buf)


    # Strange behaviour
    def get_data_ready(self):
        buf = self.fill_cmd_send_buf_no_crc(self.CMD_GET_DATA_READY, []);

        self.io.i2c_write(buf);


    # Strange behaviour
    def set_temperature_offset(self, temperature_offset):
        BUF_SIZE = self.COMMAND_LEN + self.WORD_LEN + self.CRC8_LEN;
        buf = self.fill_cmd_send_buf(self.CMD_SET_TEMPERATURE_OFFSET, [temperature_offset])
        self.io.i2c_write(buf)


    # TESTE ADN WORKS!
    def set_altitude(self, altitude):
        BUF_SIZE = self.COMMAND_LEN + self.WORD_LEN + self.CRC8_LEN;
        buf = self.fill_cmd_send_buf(self.CMD_SET_ALTITUDE, [altitude])
        self.io.i2c_write(buf)


    # TESTE ADN WORKS!
    def get_configured_address(self):
        return self.io.get_configured_address()
