# SCD30-Raspberry-Pi
Python library for Raspberry pi and the SCD30 sensor.
More information about the sensor : https://www.sensirion.com/en/environmental-sensors/carbon-dioxide-sensors-co2/

# Hardware Bug on RPI
The Raspberry pi has a Hardware bug makes communication with slave i2c devices impossible.
See https://github.com/raspberrypi/linux/issues/254
Use i2c-gpio overlay instead of the Raspberry pi Hardware implementation of i2c.
See https://raspberrypi.stackexchange.com/questions/37796/how-to-use-i2c-gpio-with-raspberry-pi
<br />
Some of the function of this library are not fully implemented or buggy.
