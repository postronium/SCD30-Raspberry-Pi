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

import io


I2C_ADDRESS = 0x61

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

# data : array of bytes
# count : length of array
# TESTED
def generate_crc(data, count):
    crc = CRC8_INIT
    # calculates 8-Bit checksum with given polynomial
    for current_byte in xrange(count):
        crc ^= (data[current_byte]);
        for crc_bit in xrange(8):
            if crc & 0x80:
                crc = (crc << 1) ^ CRC8_POLYNOMIAL;
            else:
                crc = (crc << 1);
            crc = crc%255
    return crc

# TESTED
def check_crc(data, count, checksum):
    if generate_crc(data, count) != checksum :
        return STATUS_FAIL
    return STATUS_OK


# return data unsigned integer 16 bit
# data_words (unsigned integer 16 bit) unber of data words to read (without CRC bytes)
# NOT TESTED
def i2c_read_word(data_words):
    size = data_words * (WORD_LEN + CRC8_LEN)
    word_buf = [0]*MAX_BUFFER_WORDS     #not sure about it
    buf8 = [0]*MAX_BUFFER_WORDS         #not sure about it

    ret = io.i2c_read(I2C_ADDRESS, buf8, size)
    if ret != STATUS_OK:
        return ret


    # check the CRC for each word
    i = 0
    j = 0
    while(i < size):
        if check_crc(buf8[i:i+WORD_LEN], WORD_LEN, buf8[i + WORD_LEN]) == STATUS_FAIL :
            return STATUS_FAIL

        data[j] = buf8[i]
        data[j + 1] = buf8[i + 1]

        i += WORD_LEN + CRC8_LEN
        j += WORD_LEN

    return STATUS_OK
