from scd30 import SCD30

sensor = SCD30()



data = sensor.get_data_ready()

print("result:")
for byte in data:
    print(byte)
