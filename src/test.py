from scd30 import SCD30

sensor = SCD30()



# CRC test
# crc = sensor.generate_crc([253, 235], 2)
# print("The CRC is : " + str(crc))
# print(sensor.check_crc([253, 235], 2, crc))



data = sensor.read_measurement()

print("result:")
for byte in data:
    print(byte)
