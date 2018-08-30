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

from dummyScd30IO import SCD30IO

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

    # data : array of bytes
    # count : length of array
    # TESTED
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
                crc = crc%255
        return crc

    # TESTED
    def check_crc(self, data, count, checksum):
        if self.generate_crc(data, count) != checksum :
            return self.STATUS_FAIL
        return self.STATUS_OK


    # return data unsigned integer 16 bit
    # data_words (unsigned integer 16 bit) unber of data words to read (without CRC bytes)
    # NOT TESTED
    def i2c_read_words(self, data, num_words):
        size = num_words * (self.WORD_LEN + self.CRC8_LEN)
        word_buf = [0]*self.MAX_BUFFER_WORDS     #not sure about it
        buf8 = [0]*self.MAX_BUFFER_WORDS         #not sure about it

        ret = self.io.i2c_read(buf8, size)
        if ret != self.STATUS_OK:
            return ret


        # check the CRC for each word
        i = 0
        j = 0
        while(i < size):
            if self.check_crc(buf8[i:i+self.WORD_LEN], self.WORD_LEN, buf8[i + self.WORD_LEN]) == self.STATUS_FAIL :
                return self.STATUS_FAIL

            data[j] = buf8[i]
            data[j + 1] = buf8[i + 1]

            i += self.WORD_LEN + self.CRC8_LEN
            j += self.WORD_LEN

        return self.STATUS_OK

    # return the buffer
    # NOT TESTED
    def fill_cmd_send_buf(self, cmd, args):
        BUF_SIZE = self.COMMAND_LEN + (self.WORD_LEN + self.CRC8_LEN)*1;
        BUF_SIZE = 3;
        idx = 0
        buf = [0]*BUF_SIZE

        #store cmd in buffer
        buf[idx] = ((cmd & 0xFF00) >> 8)%256
        idx += 1
        buf[idx] = ((cmd & 0x00FF) >> 0)%256
        idx += 1

        for arg in args:
            #not sure about this (what does the function be16_to_cpu ?)
            #generate crc for the arg
            word = [0]*2
            word[0] = ((arg & 0xFF00) >> 8)%256
            word[1] = ((arg & 0x00FF) >> 0)%256
            crc = self.generate_crc(word, self.WORD_LEN)

            #store the arg with the crc in buffer
            buf[idx] = word[0]
            idx += 1
            buf[idx] = word[1]
            idx += 1
            buf[idx] = crc
            idx += 1

        print(buf)
        return buf


    # NOT TESTED
    def i2c_write(self, command):
        buf = self.fill_cmd_send_buf(command, []);
        #not sure about this (whats the register address (not the device address)?)

        return self.io.i2c_write(buf);


    # NOT TESTED
    # This function reads data words from the sensor after a command has been issued
    def i2c_read_words_from_cmd(self, cmd, data_words, num_words):
        ret = self.i2c_write(cmd)

        if ret != self.STATUS_OK :
            print("error")
            return ret

        return self.i2c_read_words(data_words, num_words)



    # NOT TESTED
    # ambient_pressure_mbar is an u16 array
    def start_periodic_measurement(self, ambient_pressure_mbar):
        BUF_SIZE = self.COMMAND_LEN + self.WORD_LEN + self.CRC8_LEN;

        if ambient_pressure_mbar and (
                ambient_pressure_mbar < 700 or
                ambient_pressure_mbar > 1400):
            # out of allowable range
            return self.STATUS_FAIL

        buf = self.fill_cmd_send_buf(self.CMD_START_PERIODIC_MEASUREMENT, [ambient_pressure_mbar])

        return self.io.i2c_write(buf)

    # NOT TESTED
    def stop_periodic_measurement(self):
        return self.i2c_write(self.CMD_STOP_PERIODIC_MEASUREMENT)


    # NOT TESTED
    def read_measurement(self, data):
        word_buf = [0]*6 # 2 words for each co2, temperature, humidity
        ret = self.i2c_read_words_from_cmd(self.CMD_READ_MEASUREMENT, word_buf,
                len(word_buf) / self.WORD_LEN)

        if ret != self.STATUS_OK:
            return ret

        #TODO special treatement to convert to float 32
        data[CO2_DATA_INDEX] = (word_buf[0] << 16) | word_buf[1]
        data[TEMP_DATA_INDEX] = (word_buf[2] << 16) | word_buf[3]
        data[HUMIDITY_DATA_INDEX] = (word_buf[4] << 16) | word_buf[5]

        return self.STATUS_OK


    # NOT TESTED
    #interval is an u16 integer
    def set_measurement_interval(self, interval_sec):
        BUF_SIZE = self.COMMAND_LEN + self.WORD_LEN + self.CRC8_LEN;

        if interval_sec < 2 or interval_sec > 1800:
            return self.STATUS_FAIL

        buf = self.fill_cmd_send_buf(self.CMD_SET_MEASUREMENT_INTERVAL, [interval_sec])
        return self.io.i2c_write(0, buf, BUF_SIZE)


    # NOT TESTED
    def get_data_ready(self, data_ready):
        return self.i2c_read_words_from_cmd(self.CMD_GET_DATA_READY, data_ready,
                                           len(data_ready) / self.WORD_LEN)


    # NOT TESTED
    def set_temperature_offset(self, temperature_offset):
        BUF_SIZE = self.COMMAND_LEN + self.WORD_LEN + self.CRC8_LEN;
        buf = self.fill_cmd_send_buf(self.CMD_SET_TEMPERATURE_OFFSET, [temperature_offset])
        return self.io.i2c_write(0, buf, BUF_SIZE)


    # NOT TESTED
    def set_altitude(self, altitude):
        BUF_SIZE = self.COMMAND_LEN + self.WORD_LEN + self.CRC8_LEN;
        buf = self.fill_cmd_send_buf(self.CMD_SET_ALTITUDE, [altitude])
        return self.io.i2c_write(0, buf, BUF_SIZE)


    # NOT TESTED
    def get_configured_address(self):
        return self.io.get_configured_address()



    # NOT TESTED
    def scd_probe(self):
        self.io.i2c_init()
        return self.get_data_ready([0])
