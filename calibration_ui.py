#!/usr/bin/env python3
import sys
import json
import time
import subprocess  # Import subprocess to launch Onboard
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, 
    QLineEdit, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QDoubleValidator  # Import QDoubleValidator for numeric input
from hx711_reader import LoadCell  # Import the load cell sensor class
from ui import WeightDisplay  # Import the WeightDisplay class


class CalibrationUI(QWidget):
    def __init__(self):
        """Initialize the Calibration UI"""
        super().__init__()
        self.setWindowTitle("Load Cell Calibration")
        self.setGeometry(200, 200, 500, 400)
        self.showMaximized()  # Maximize the window but keep the menu bar visible

        # Load Cell Instance
        self.load_cell = LoadCell()

        # UI Components
        self.instructions = QLabel(
            "Calibration steps:\n"
            "1. Click 'Tare' with no weight to set the zero point.\n"
            "2. Place a known weight on the scale and enter its value.\n"
            "3. Click 'Compute Calibration' to calculate the calibration constants.\n"
            "4. Save the calibration for future use."
        )
        self.instructions.setWordWrap(True)

        self.exit_button = QPushButton("X")
        self.exit_button.setFixedSize(70, 70)
        self.exit_button.setStyleSheet("font-size: 18px; background-color: red; color: white;")
        self.exit_button.clicked.connect(self.return_to_main_ui)

        self.tare_button = QPushButton("Tare Scale")
        self.tare_button.clicked.connect(self.tare_scale)

        self.label_zero = QLabel("Tare Offset: Not Captured")

        self.input_weight = QLineEdit()
        self.input_weight.setPlaceholderText("Enter known weight (grams)")
        self.input_weight.setValidator(QDoubleValidator(0.0, 9999.99, 2))  # Allow only numbers with up to 2 decimals
        self.input_weight.setInputMethodHints(Qt.ImhPreferNumbers)
        self.input_weight.setFixedSize(200, 40)  # Set a taller and less wide text box

        self.capture_button = QPushButton("Capture Known Weight")
        self.capture_button.clicked.connect(self.capture_known_weight)

        self.label_known_weight = QLabel("Known Weight Raw: Not Captured")

        self.compute_button = QPushButton("Compute Calibration")
        self.compute_button.clicked.connect(self.compute_calibration)

        self.live_reading_label = QLabel("Live Reading: 0.00 g")

        self.save_button = QPushButton("Save Calibration")
        self.save_button.setVisible(True)
        self.save_button.clicked.connect(self.save_calibration)

        # Set uniform width for buttons and text boxes
        uniform_width = 200
        self.tare_button.setFixedSize(uniform_width, 40)
        self.input_weight.setFixedSize(uniform_width, 40)
        self.compute_button.setFixedSize(uniform_width, 40)
        self.capture_button.setFixedSize(uniform_width, 40)
        self.save_button.setFixedSize(uniform_width, 40)

        # Layout
        layout = QVBoxLayout()

        # Create a grid layout for two columns
        grid_layout = QHBoxLayout()

        # Left column
        left_column = QVBoxLayout()
        left_column.addWidget(self.tare_button, alignment=Qt.AlignTop)
        left_column.addWidget(self.input_weight, alignment=Qt.AlignTop)
        left_column.addWidget(self.compute_button, alignment=Qt.AlignTop)

        # Right column
        right_column = QVBoxLayout()
        right_column.addSpacing(40)  # Add blank space at the top
        right_column.addWidget(self.capture_button, alignment=Qt.AlignTop)
        right_column.addWidget(self.save_button, alignment=Qt.AlignTop)

        # Add columns to the grid layout
        grid_layout.addLayout(left_column)
        grid_layout.addLayout(right_column)

        # Add the grid layout to the main layout
        layout.addLayout(grid_layout)

        layout.addWidget(self.label_zero, alignment=Qt.AlignTop)
        layout.addWidget(self.label_known_weight, alignment=Qt.AlignTop)
        layout.addWidget(self.live_reading_label, alignment=Qt.AlignTop)

        # Move instructions to the bottom
        layout.addWidget(self.instructions, alignment=Qt.AlignBottom)

        # Add the red "X" button to the bottom right
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()  # Add stretch to push the button to the right
        bottom_layout.addWidget(self.exit_button, alignment=Qt.AlignRight)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        # Variables
        self.offset = None
        self.known_weight_raw = None
        self.A = None
        self.B = None

        # Timer to update live reading
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_live_reading)
        self.timer.start(500)

    def tare_scale(self):
        """Zero the scale and set the tare offset."""
        self.load_cell.tare()
        self.offset = self.load_cell.offset
        self.label_zero.setText(f"Tare Offset: {self.offset:.2f}")

    def capture_known_weight(self):
        """Capture the raw reading for the known weight."""
        self.known_weight_raw = self.load_cell.get_raw()
        self.label_known_weight.setText(f"Known Weight Raw: {self.known_weight_raw:.2f}")

    def compute_calibration(self):
        """Calculate calibration factors based on the zero point and known weight."""
        try:
            weight = float(self.input_weight.text())

            if self.offset is None or self.known_weight_raw is None:
                QMessageBox.warning(self, "Error", "Tare the scale and capture the known weight first.")
                return

            # Adjust raw reading by tare offset
            raw_adjusted = self.known_weight_raw - self.offset

            print(f"[DEBUG] Raw Adjusted: {raw_adjusted:.2f}, Known Weight: {weight:.2f}")

            # Compute calibration formula (A = slope, B = intercept)
            self.A = weight / raw_adjusted
            self.B = 0  # Set B to 0 since we are using a single point calibration

            print(f"[DEBUG] Calibration Factors - A: {self.A}, B: {self.B}")

            # Update the load cell calibration
            self.load_cell.A = self.A
            self.load_cell.B = self.B

            # Update the live reading label with the new calibrated value
            weight = self.load_cell.get_weight(5)
            self.live_reading_label.setText(f"Live Reading: {weight:.2f} g")

            QMessageBox.information(self, "Success", "Calibration computed and applied. Click 'Save Calibration' if correct.")
            self.save_button.setVisible(True)

        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid weight.")

    def update_live_reading(self):
        """Show a live weight reading for verification."""
        weight = self.load_cell.get_weight(5)
        self.live_reading_label.setText(f"Live Reading: {weight:.2f} g")

    def save_calibration(self):
        """Save calibration to a file."""
        if self.A is None:
            QMessageBox.warning(self, "Error", "Compute calibration before saving.")
            return

        calibration_data = {
            "offset": self.offset,
            "A": self.A,
            "B": self.B
        }

        with open("calibration.json", "w") as file:
            json.dump(calibration_data, file)

        self.load_cell.save_calibration()
        if hasattr(self, 'save_calibration_callback'):
            self.save_calibration_callback()  # Trigger callback to reload calibration

        QMessageBox.information(self, "Success", "Calibration saved!")

    def return_to_main_ui(self):
        """Return to the UI window."""
        if hasattr(self, 'ui_window') and self.ui_window is not None:
            self.ui_window.main_ui_window = self.main_ui_window  # Pass the MainUI instance back to WeightDisplay
            self.ui_window.show()  # Reuse the existing WeightDisplay instance
        else:
            self.ui_window = WeightDisplay()  # Create a new WeightDisplay instance if none exists
            self.ui_window.main_ui_window = self.main_ui_window  # Pass the MainUI instance to the new WeightDisplay
            self.ui_window.show()
        self.close()  # Close the current CalibrationUI window
        self.deleteLater()  # Ensure the current instance is deleted to avoid lingering references


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalibrationUI()
    window.show()
    sys.exit(app.exec_())
