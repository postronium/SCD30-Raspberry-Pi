import scd30

# CRC test
#crc = scd30.generate_crc([0, 1, 2, 255, 4, 5, 255, 255, 128, 128, 128, 128, 128, 128, 128], 15)
#print("The CRC is : " + str(crc))
#print(scd30.check_crc([0, 1, 2, 255, 4, 5, 255, 255, 128, 128, 128, 128, 128, 128, 128], 15, crc))

size = 10
i = 0
while(i < size):
    print(i)
    i += 1
