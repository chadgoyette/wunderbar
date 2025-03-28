#!/usr/bin/env python3
import sys
import threading
import time
import RPi.GPIO as GPIO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QComboBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QTimer
from hx711_reader import LoadCell  # Load cell sensor class
from motor import BLDCMotor  # Motor control class
from settings_ui import SettingsWindow  # Settings window
import settings

class WeightDisplay(QWidget):
    def __init__(self):
        """Initialize the main UI window and components."""
        super().__init__()

        # Load stored settings
        self.app_settings = settings.load_settings()

        # Initialize Load Cell (Weight Sensor)
        self.load_cell = LoadCell(calibration_factor=0.002965)

        # Initialize Motor Controller
        GPIO.setmode(GPIO.BCM)
        self.motor = BLDCMotor(pwm_pin=5, speed_pin=16, en_pin=20, brk_pin=19)
        self.motor_speed = self.app_settings["rotor_speed"]

        # UI Elements
        self.weight_label = QLabel("Weight:  0.00 g", self)  # Add padding to align text
        self.weight_label.setAlignment(Qt.AlignCenter)
        self.weight_label.setStyleSheet(
            """
            font-size: 40px;
            font-family: 'Courier New', monospace;  /* Use fixed-width font */
            font-weight: bold;
        """
        )

        self.speed_label = QLabel(f"Motor Speed: {self.motor_speed}%", self)
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.rpm_label = QLabel("RPM: 0", self)
        self.rpm_label.setAlignment(Qt.AlignCenter)
        self.rpm_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        # Buttons
        self.calibration_button = QPushButton("Load Cell Calibration", self)
        self.calibration_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #444; color: white;")
        self.calibration_button.clicked.connect(self.open_calibration_ui)

        self.tare_button = QPushButton("Tare", self)
        self.tare_button.setStyleSheet("font-size: 20px; padding: 10px;")
        self.tare_button.clicked.connect(self.tare_scale)

        self.start_motor_button = QPushButton("Start Motor", self)
        self.start_motor_button.setStyleSheet("font-size: 20px; padding: 10px;")
        self.start_motor_button.clicked.connect(self.start_motor)

        self.stop_motor_button = QPushButton("Stop Motor", self)
        self.stop_motor_button.setStyleSheet("font-size: 20px; padding: 10px; background-color: red; color: white;")
        self.stop_motor_button.clicked.connect(self.stop_motor)

        self.increase_speed_button = QPushButton("Increase Speed", self)
        self.increase_speed_button.setStyleSheet("font-size: 20px; padding: 10px;")
        self.increase_speed_button.clicked.connect(self.increase_speed)

        self.decrease_speed_button = QPushButton("Decrease Speed", self)
        self.decrease_speed_button.setStyleSheet("font-size: 20px; padding: 10px;")
        self.decrease_speed_button.clicked.connect(self.decrease_speed)

        self.exit_button = QPushButton("X")
        self.exit_button.setFixedSize(70, 70)  # Adjust the size here (width, height)
        self.exit_button.setStyleSheet("font-size: 24px; padding: 5px; background-color: red; color: white;")  # Adjust font size if needed
        self.exit_button.clicked.connect(self.return_to_main_screen)  # Updated behavior

        # Motor Speed Section
        motor_speed_layout = QGridLayout()  # Use QGridLayout for precise positioning

        # Remove the motor speed label
        # motor_speed_label = QLabel("Motor Speed (%)")
        # motor_speed_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        # motor_speed_layout.addWidget(motor_speed_label, 0, 0, Qt.AlignLeft)

        # Remove the spinbox
        # motor_speed_layout.addWidget(self.motor_speed_spinbox, 1, 0, Qt.AlignLeft)

        # Add Save Speed Button
        self.save_speed_button = QPushButton("Save Speed", self)
        self.save_speed_button.setStyleSheet("font-size: 20px; padding: 10px; background-color: green; color: white;")
        self.save_speed_button.clicked.connect(self.save_motor_speed)

        self.save_tare_button = QPushButton("Save Tare", self)  # New button for saving tare
        self.save_tare_button.setStyleSheet("font-size: 20px; padding: 10px; background-color: green; color: white;")
        self.save_tare_button.clicked.connect(self.save_tare)

        # Grid layout for buttons
        button_layout = QGridLayout()
        button_layout.setSpacing(10)  # Add spacing between buttons

        # Add buttons to the grid layout
        button_layout.addWidget(self.calibration_button, 0, 0)  # Row 0, Column 0
        button_layout.addWidget(self.exit_button, 0, 1, alignment=Qt.AlignRight)  # Row 0, Column 1
        button_layout.addWidget(self.tare_button, 1, 0)  # Row 1, Column 0
        button_layout.addWidget(self.start_motor_button, 1, 1)  # Row 1, Column 1
        button_layout.addWidget(self.stop_motor_button, 2, 0)  # Row 2, Column 0
        button_layout.addWidget(self.increase_speed_button, 2, 1)  # Row 2, Column 1
        button_layout.addWidget(self.decrease_speed_button, 3, 0)  # Row 3, Column 0
        button_layout.addWidget(self.save_speed_button, 3, 1)  # Row 3, Column 1
        button_layout.addWidget(self.save_tare_button, 4, 0)  # Add Save Tare button to the grid layout

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # Add margins around the layout
        layout.setSpacing(10)  # Add spacing between widgets

        layout.addWidget(self.weight_label)
        layout.addWidget(self.speed_label)
        layout.addWidget(self.rpm_label)
        layout.addLayout(button_layout)  # Add the button grid layout to the main layout
        layout.addStretch()  # Add a spacer to push content higher

        self.setLayout(layout)

        # Timer to update weight display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weight)
        self.timer.start(50)

        # Thread for RPM updates
        self.rpm_thread_running = True  # Flag to control the RPM thread
        self.rpm_thread = threading.Thread(target=self.rpm_loop, daemon=True)
        self.rpm_thread.start()

        # Configure Window
        self.setWindowTitle("Weight Sensor & Motor Control")
        self.setGeometry(0, 0, 800, 480)
        self.showFullScreen()

        # Callback to notify MainUI of changes
        self.save_motor_speed_callback = None

    def update_weight(self):
        """Update weight from load cell."""
        weight = self.load_cell.get_weight()
        self.weight_label.setText(f"Weight: {weight:6.2f} g")  # Pad to 6 characters for alignment

    def rpm_loop(self):
        """Continuously update RPM in a separate thread."""
        while self.rpm_thread_running:
            rpm = self.motor.get_rpm()  # This is rotor RPM
            if self.rpm_thread_running:
                self.rpm_label.setText(f"RPM: {rpm:.2f}")  # Display rotor RPM
            time.sleep(0.3)

    def load_size_settings(self):
        """Load ingredient weight settings based on selected flavor."""
        flavor = self.flavor_dropdown.currentText()
        size_settings = self.app_settings["sizes"].get(flavor, {})
        print(f"[INFO] Loaded {flavor} settings: {size_settings}")

    def tare_scale(self):
        """Tare (zero) the scale."""
        self.weight_label.setText("Taring...")
        QApplication.processEvents()
        self.load_cell.tare()  # Perform taring
        weight = self.load_cell.get_weight(5)  # Get the corrected weight after taring
        self.weight_label.setText(f"Weight: {weight:6.2f} g")  # Update the label with the corrected weight
        print(f"[INFO] Scale tared. Current weight: {weight:.2f} g")

    def start_motor(self):
        """Start the motor at stored speed."""
        self.motor.start()
        self.motor_speed = self.app_settings["rotor_speed"]
        self.motor.set_speed(self.motor_speed)
        self.speed_label.setText(f"Motor Speed: {self.motor_speed}%")
        QApplication.processEvents()

    def stop_motor(self):
        """Stop the motor completely."""
        self.motor.stop()
        self.speed_label.setText(f"Motor Speed: {self.motor_speed}%")  # Keep the motor speed setting displayed
        QApplication.processEvents()

    def increase_speed(self):
        """Increase motor speed by 10% (max 100%)."""
        if self.motor_speed < 100:
            self.motor_speed += 10
            self.motor.set_speed(self.motor_speed)
            self.speed_label.setText(f"Motor Speed: {self.motor_speed}%")
            QApplication.processEvents()

    def decrease_speed(self):
        """Decrease motor speed by 10% (min 0%)."""
        if self.motor_speed > 0:
            self.motor_speed -= 10
            self.motor.set_speed(self.motor_speed)
            self.speed_label.setText(f"Motor Speed: {self.motor_speed}%")
            QApplication.processEvents()

    def return_to_main_screen(self):
        """Return to the main UI start screen."""
        self.close()  # Close the current WeightDisplay window
        if hasattr(self, 'main_ui_window') and self.main_ui_window is not None:
            self.main_ui_window.show()  # Reuse the existing MainUI instance
        else:
            print("[ERROR] MainUI instance not found. Ensure MainUI is initialized before opening WeightDisplay.")

    def save_motor_speed(self):
        """Save the updated motor speed to settings.json."""
        self.app_settings["rotor_speed"] = self.motor_speed
        settings.save_settings(self.app_settings)
        print(f"[INFO] Motor speed updated to {self.motor_speed}% and saved.")
        if self.save_motor_speed_callback:
            self.save_motor_speed_callback()  # Notify MainUI to reload settings
        QApplication.processEvents()

    def save_tare(self):
        """Tare the scale and save the offset."""
        self.load_cell.tare()  # Perform taring
        print("[INFO] Tare offset saved.")

    def open_calibration_ui(self):
        """Open the Load Cell Calibration UI."""
        from calibration_ui import CalibrationUI  # Import the CalibrationUI class
        self.calibration_window = CalibrationUI()  # Create a new CalibrationUI instance
        self.calibration_window.ui_window = self  # Pass the current WeightDisplay instance to CalibrationUI
        self.calibration_window.main_ui_window = self.main_ui_window  # Pass the MainUI instance to CalibrationUI
        self.calibration_window.show()
        self.hide()  # Hide the current WeightDisplay window instead of closing it

    def closeEvent(self, event):
        """Handle the window close event."""
        self.rpm_thread_running = False  # Stop the RPM thread
        if self.rpm_thread.is_alive():
            self.rpm_thread.join()  # Wait for the thread to finish
        super().closeEvent(event)  # Call the parent class's closeEvent

    def closeProgram(self):
        """Safely close the program and cleanup GPIO."""
        self.motor.cleanup()
        self.load_cell.stop()
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeightDisplay()
    sys.exit(app.exec_())



