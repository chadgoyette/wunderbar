import pigpio
import time
import threading
import RPi.GPIO as GPIO

class BLDCMotor:
    def __init__(self, pwm_pin, speed_pin, en_pin, brk_pin, motor_pulley_diameter=22, rotor_pulley_diameter=95, dir_pin=12):
        self.pwm_pin = pwm_pin
        self.speed_pin = speed_pin
        self.en_pin = en_pin
        self.brk_pin = brk_pin
        self.dir_pin = dir_pin  # Direction control pin
        self.motor_pulley_diameter = motor_pulley_diameter
        self.rotor_pulley_diameter = rotor_pulley_diameter
        self.pulse_count = 0
        self.lock = threading.Lock()
        self.was_interrupted = False

        # Safety interlock setup
        self.interlock_pin = 25
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.interlock_pin, GPIO.IN)

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise Exception("Could not connect to pigpio daemon!")

        self.pi.set_mode(self.pwm_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.speed_pin, pigpio.INPUT)
        self.pi.set_mode(self.en_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.brk_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.dir_pin, pigpio.OUTPUT)  # Configure direction pin as output

        self.pi.write(self.en_pin, 1)
        self.pi.write(self.brk_pin, 1)
        self.pi.set_PWM_frequency(self.pwm_pin, 4000)

        # Set direction pin to HIGH permanently
        self.pi.write(self.dir_pin, 0)  # Set GPIO-12 HIGH permanently
        print("[INFO] Motor direction permanently set to HIGH (GPIO-12 HIGH).")

        self.callback = self.pi.callback(self.speed_pin, pigpio.RISING_EDGE, self._pulse_callback)

        print("[INFO] BLDC Motor initialized.")

    def _pulse_callback(self, gpio, level, tick):
        with self.lock:
            self.pulse_count += 1

    def interlock_triggered(self):
        """Check if the safety interlock (lid) is triggered."""
        return GPIO.input(self.interlock_pin) == GPIO.HIGH

    def check_interlock_and_stop(self):
        """Stop the motor if the interlock is triggered."""
        if self.interlock_triggered():
            print("[SAFETY] Cover removed! Stopping motor...")
            self.stop()
            self.was_interrupted = True

    def set_speed(self, duty_cycle):
        """Set the motor speed, ensuring the interlock is not triggered."""
        if self.interlock_triggered():
            print("[WARNING] Cover open! Motor speed set request ignored.")
            self.was_interrupted = True
            return
        if 0 <= duty_cycle <= 100:
            pwm_value = int((duty_cycle / 100.0) * 255)
            self.pi.set_PWM_dutycycle(self.pwm_pin, pwm_value)
            actual_freq = self.pi.get_PWM_frequency(self.pwm_pin)
            actual_duty = self.pi.get_PWM_dutycycle(self.pwm_pin)
            print(f"[INFO] Motor Speed: {duty_cycle}% | PWM: {pwm_value}/255 | Freq: {actual_freq} Hz | Duty Confirmed: {actual_duty}")
        else:
            raise ValueError("Duty cycle must be between 0 and 100.")

    def start(self):
        """Start the motor, ensuring the interlock is not triggered."""
        if self.interlock_triggered():
            print("[WARNING] Cannot start motor: Cover is open.")
            self.was_interrupted = True
            return False

        print("[INFO] Starting motor...")
        try:
            if self.pi is None or not self.pi.connected:
                print("[ERROR] pigpio connection lost. Reinitializing...")
                self.pi = pigpio.pi()
                if not self.pi.connected:
                    raise RuntimeError("Failed to reconnect to pigpio daemon.")

            print("[DEBUG] Enabling motor and releasing brake...")
            self.callback = self.pi.callback(self.speed_pin, pigpio.RISING_EDGE, self._pulse_callback)  # Reinitialize callback
            self.pulse_count = 0  # Reset pulse count to ensure accurate RPM calculation

            self.pi.write(self.en_pin, 0)
            self.pi.write(self.brk_pin, 0)
            time.sleep(0.5)  # Allow motor to stabilize before RPM calculation
            print("[INFO] Motor enabled and brake released.")
            return True
        except Exception as e:
            print(f"[ERROR] Exception occurred while starting motor: {e}")
            return False

    def get_rpm(self, sample_time=1.0):
        with self.lock:
            start_count = self.pulse_count
        time.sleep(sample_time)
        with self.lock:
            end_count = self.pulse_count

        pulses = end_count - start_count
        frequency = pulses / sample_time
        motor_rpm = (frequency / 2) * (60 / 3)  # Motor RPM calculation
        pulley_ratio = self.rotor_pulley_diameter / self.motor_pulley_diameter
        rotor_rpm = motor_rpm / pulley_ratio  # Convert motor RPM to rotor RPM
        correction_factor = 1.031
        return rotor_rpm * correction_factor  # Return rotor RPM

    def stop(self):
        """Stop the motor and clean up resources."""
        self.pi.write(self.brk_pin, 1)
        self.pi.write(self.en_pin, 1)
        if hasattr(self, 'callback') and self.callback is not None:
            self.callback.cancel()
        self.pi.set_servo_pulsewidth(self.pwm_pin, 0)
        self.pi.stop()
        print("[INFO] Motor stopped and resources cleaned up.")

    def debug_status(self):
        print("[DEBUG] EN:", self.pi.read(self.en_pin))
        print("[DEBUG] BRK:", self.pi.read(self.brk_pin))
        print("[DEBUG] PWM duty:", self.pi.get_PWM_dutycycle(self.pwm_pin))
        print("[DEBUG] Interlock:", self.interlock_triggered())
