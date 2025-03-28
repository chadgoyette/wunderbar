from hx711_reader import LoadCell
import time

print("Waiting 2 seconds for HX711 to settle...")
time.sleep(2)

lc = LoadCell()
lc.tare()
print("Tare done. Reading weight...")
while True:
    print("Weight:", lc.get_weight())
    time.sleep(1)
