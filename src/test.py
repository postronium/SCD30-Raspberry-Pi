from scd30 import SCD30

sensor = SCD30()



data = sensor.read_measurement()

print("result:")
for byte in data:
    print(byte)
