from PySide6.QtCore import QObject, Slot
from motor import BLDCMotor

class MotorController(QObject):
    def __init__(self):
        super().__init__()
        # Set your GPIO pin numbers here
        self.motor = BLDCMotor(
            pwm_pin=18,         # adjust as needed
            speed_pin=16,
            en_pin=20,
            brk_pin=19
        )
        self.default_speed = 60  # default duty cycle %

    @Slot()
    def start_motor(self):
        print("[INFO] Attempting to start motor...")
        if self.motor.interlock_triggered():
            print("[ERROR] Cannot start motor: Interlock is triggered (cover open).")
            return

        try:
            print("[DEBUG] Checking motor initialization...")
            if self.motor.start():
                print("[DEBUG] Motor started successfully, setting speed...")
                self.motor.set_speed(self.default_speed)
                print("[INFO] Motor started successfully.")
            else:
                print("[ERROR] Motor failed to start.")
        except Exception as e:
            print(f"[ERROR] Exception occurred while starting motor: {e}")

    @Slot()
    def stop_motor(self):
        print("[INFO] Attempting to stop motor...")
        self.motor.stop()
        print("[INFO] Motor stopped successfully.")

    @Slot(result=bool)
    def interlock_triggered(self):
        return self.motor.interlock_triggered()
