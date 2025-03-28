#!/usr/bin/env python3
import time
import json
import RPi.GPIO as GPIO
from hx711 import HX711 # type: ignore

class LoadCell:
    def __init__(self, calibration_factor=0.002965, cal_file="calibration.json"):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.hx = HX711(18, 17)
        self.cal_file = cal_file
        self.A = calibration_factor
        self.B = 0
        self.offset = 0

        self.load_calibration()   # ← Moved up
        #self.tare()               # ← Now runs after loading

    def tare(self, samples=60):
        """Zero the scale and set the tare offset."""
        print("[INFO] Taring the scale... Make sure it's empty and stable.")

        readings = []
        for _ in range(samples):
            reading = self.hx.get_weight_A(1)
            if reading == -1.0:
                print("[WARNING] Invalid -1.0 reading detected. Retrying...")
                time.sleep(0.1)
                continue
            readings.append(reading)
            time.sleep(0.05)

        if not readings:
            print("[ERROR] No valid readings during tare!")
            return

        # Set the offset and reset B to 0
        self.offset = sum(readings) / len(readings)
        self.B = 0  # Reset B to ensure the scale reads 0.00g after taring
        print(f"[DEBUG] New Offset Set: {self.offset:.2f}, B Reset to: {self.B}")

        # Save and reload calibration to ensure the updated offset is applied
        self.save_calibration()
        self.load_calibration()

        # Test the reading after taring
        test_reading = self.get_weight(5)
        print(f"[DEBUG] Weight after tare: {test_reading:.2f} g (should be 0.00g)")
        print("[INFO] Tare complete.")

    def get_raw(self, samples=5):
        """Return an average raw reading from the load cell."""
        readings = []
        for _ in range(samples):
            reading = self.hx.get_weight_A(1)
            if reading != -1.0:  # Ignore invalid readings
                readings.append(reading)
            time.sleep(0.05)

        if not readings:
            print("[ERROR] No valid readings!")
            return 0.0

        return sum(readings) / len(readings)


    def get_weight(self, samples=5):
        """Returns a stable weight reading using a moving average filter."""
        raw_values = []
        retries = 3  # Retry up to 3 times for valid readings
        for _ in range(samples):
            for attempt in range(retries):
                reading = self.get_raw(1)
                if reading != -1.0:  # Ignore invalid readings
                    raw_values.append(reading)
                    break
                else:
                    print(f"[WARNING] Invalid reading detected. Retrying ({attempt + 1}/{retries})...")
                    time.sleep(0.05)

        if not raw_values:
            print("[ERROR] No valid readings after retries!")
            return 0.0

        avg_raw = sum(raw_values) / len(raw_values)
        adjusted = avg_raw - self.offset
        weight = self.A * adjusted + self.B
        #print(f"[DEBUG] Raw: {avg_raw:.2f}, Adjusted: {adjusted:.2f}, Weight: {weight:.2f}")
        return max(round(weight, 2), 0.0)  # Ensure no negative weights

    def calibrate_points(self, raw1, raw2, weight1, weight2):
        """
        Perform a two-point calibration.
        raw1 and raw2 are the raw readings (after subtracting the offset)
        corresponding to known weights weight1 and weight2 (in grams).
        """
        raw1 -= self.offset  # Adjust raw readings by tare offset
        raw2 -= self.offset

        if raw2 == raw1:
            raise ValueError("Calibration raw values must differ.")

        # Calculate slope (A) and intercept (B)
        self.A = (weight2 - weight1) / (raw2 - raw1)
        self.B = weight1 - self.A * raw1
        print(f"[INFO] New calibration: A = {self.A}, B = {self.B}")
        self.save_calibration()

    def set_calibration(self, raw1, raw2, weight1, weight2):
        """
        Set calibration points programmatically.
        raw1 and raw2 are the raw readings (after subtracting the offset)
        corresponding to known weights weight1 and weight2 (in grams).
        """
        try:
            raw1 -= self.offset  # Adjust raw readings by tare offset
            raw2 -= self.offset

            if raw2 == raw1:
                raise ValueError("Calibration raw values must differ.")

            self.A = (weight2 - weight1) / (raw2 - raw1)
            self.B = weight1 - self.A * raw1
            print(f"[INFO] Calibration set - A: {self.A}, B: {self.B}")
            self.save_calibration()

        except Exception as e:
            print(f"[ERROR] Failed to set calibration: {e}")

    def save_calibration(self):
        """Save calibration values to a JSON file with proper error handling."""
        data = {
            "offset": self.offset,
            "A": self.A,
            "B": self.B
        }
        try:
            with open(self.cal_file, "w") as f:
                json.dump(data, f)
            print(f"[INFO] Calibration saved to {self.cal_file}")
        except Exception as e:
            print(f"[ERROR] Failed to save calibration: {e}")
        if hasattr(self, 'reload_calibration_callback'):
            self.reload_calibration_callback()  # Trigger callback to reload calibration

    def load_calibration(self):
        """Load calibration values from a JSON file, if available."""
        try:
            with open(self.cal_file, "r") as f:
                data = json.load(f)

            self.offset = data.get("offset", self.offset)
            self.A = data.get("A", self.A)
            self.B = data.get("B", self.B)

            print(f"[DEBUG] Loaded Calibration - Offset: {self.offset:.2f}, A: {self.A:.6f}, B: {self.B:.6f}")

        except FileNotFoundError:
            print(f"[INFO] No calibration file found ({self.cal_file}). Using default values.")
        except Exception as e:
            print("[ERROR] Loading calibration:", e)

    def zero(self, current_weight_oz):
        """Zero the scale based on the current weight in ounces."""
        current_weight_g = current_weight_oz * 28.35  # Convert ounces to grams
        adjusted_raw = (current_weight_g - self.B) / self.A  # Reverse the calibration formula
        self.offset += adjusted_raw  # Adjust the offset
        print(f"[INFO] Scale zeroed. New offset: {self.offset:.2f}")

    def stop(self):
        GPIO.cleanup()

if __name__ == "__main__":
    # For testing the LoadCell class
    load_cell = LoadCell()
    try:
        while True:
            weight = load_cell.get_weight(5)
            print("Weight: {:.2f} g".format(weight))
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting and cleaning up GPIO...")
        load_cell.stop()
