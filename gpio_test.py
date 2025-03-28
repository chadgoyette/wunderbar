import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define EN and BRK pins
EN_PIN = 20
BRK_PIN = 19

# Set both as outputs
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.setup(BRK_PIN, GPIO.OUT)

# Toggle EN and BRK states and print results
print("[INFO] Testing GPIO States...")
print("[INFO] Setting EN HIGH and BRK HIGH (Motor should be OFF)")
GPIO.output(EN_PIN, GPIO.HIGH)
GPIO.output(BRK_PIN, GPIO.HIGH)
time.sleep(2)

print("[INFO] Setting EN LOW and BRK LOW (Motor should be READY TO RUN)")
GPIO.output(EN_PIN, GPIO.LOW)
GPIO.output(BRK_PIN, GPIO.LOW)
time.sleep(2)

# Read and print the actual state of the pins
en_state = GPIO.input(EN_PIN)
brk_state = GPIO.input(BRK_PIN)

print(f"[DEBUG] EN Pin State: {en_state} (Expected: 0)")
print(f"[DEBUG] BRK Pin State: {brk_state} (Expected: 0)")

# Cleanup
GPIO.cleanup()

