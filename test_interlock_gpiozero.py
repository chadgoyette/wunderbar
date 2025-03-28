from gpiozero import Button
from signal import pause

INTERLOCK_PIN = 24  # GPIO pin for the interlock

def lid_opened():
    print("Interlock state: TRIGGERED (Lid Open)")

def lid_closed():
    print("Interlock state: SAFE (Lid Closed)")

interlock = Button(INTERLOCK_PIN, pull_up=True)
interlock.when_pressed = lid_opened
interlock.when_released = lid_closed

print("Testing interlock pin state. Press Ctrl+C to exit.")
pause()
