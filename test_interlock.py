import RPi.GPIO as GPIO
import time

INTERLOCK_PIN = 25  # GPIO pin for the interlock

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(INTERLOCK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Configure with pull-up resistor

    print("Testing interlock pin state. Press Ctrl+C to exit.")
    try:
        while True:
            state = GPIO.input(INTERLOCK_PIN)
            print(f"Interlock state: {'TRIGGERED (Lid Open)' if state == GPIO.HIGH else 'SAFE (Lid Closed)'}")
            print("Raw pin state:", state)

            time.sleep(0.5)  # Check state every 0.5 seconds
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
