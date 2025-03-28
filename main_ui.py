#!/usr/bin/env python3
import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QButtonGroup, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
import settings
from hx711_reader import LoadCell  # Your load cell class
from motor import BLDCMotor       # Your motor control class
from settings_ui import SettingsWindow  # Import the SettingsWindow class
from ui import WeightDisplay  # Import the WeightDisplay class

# Conversion: 1 oz ≈ 28.35 grams
GRAMS_TO_OZ = 1 / 28.35

class GaugeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0.0
        self.target = 100.0

    def setValue(self, value, target):
        self.value = value
        self.target = target
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        pen = QPen(Qt.white)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(rect.adjusted(1, 1, -1, -1))
        ratio = min(max(self.value / self.target, 0), 1) if self.target > 0 else 0
        fill_color = QColor(0, 255, 0) if ratio >= 1.0 else QColor(255, 0, 0)
        painter.setBrush(QBrush(fill_color))
        fill_height = int(ratio * rect.height())
        fill_rect = rect.adjusted(2, rect.height() - fill_height + 2, -2, -2)
        painter.drawRect(fill_rect)

class MainUI(QWidget):
    def __init__(self):
        print("[DEBUG] Initializing MainUI...")
        super().__init__()
        print("[DEBUG] Loading settings...")
        self.app_settings = settings.load_settings()
        print("[DEBUG] Initializing hardware components...")
        self.load_cell = LoadCell(calibration_factor=0.002965)  # Re-enable LoadCell initialization
        self.motor = BLDCMotor(pwm_pin=5, speed_pin=16, en_pin=20, brk_pin=19)  # Re-enable Motor initialization
        print("[DEBUG] MainUI initialized.")
        self.setWindowTitle("Ice Shaver Main UI")
        self.setFixedSize(800, 480)
        self.setStyleSheet("background-color: black; color: white;")
        self.state = 0
        self.motor_stopped = False
        self.settings_window = None  # Initialize settings window as None
        self.motor_settings_window = None  # Initialize motor settings window as None

        # --- Rotor speed display (absolute positioning) ---
        self.rotor_speed_label = QLabel(f"Rotor Speed Setting: {self.app_settings['rotor_speed']}%", self)
        self.rotor_speed_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        self.rotor_speed_label.setGeometry(20, 10, 300, 30)  # Position: (x=10, y=10), Size: (width=200, height=30)

        # --- Main layout ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- Top section: Flavor dropdown and size selection ---
        top_section = QHBoxLayout()
        top_section.setSpacing(20)

        # --- Flavor Dropdown ---
        self.flavor_dropdown = QComboBox()
        self.flavor_dropdown.addItems(list(self.app_settings["sizes"].keys()))
        self.flavor_dropdown.setFixedHeight(100)  # Increase height for better touch interaction
        self.flavor_dropdown.setStyleSheet("""
            font-size: 24px;  /* Increase font size */
            padding: 1px;   /* Add more padding */
            background-color: #444;
            color: white;
        """)
        top_section.addWidget(self.flavor_dropdown)

        # --- Size Buttons ---
        self.size_group = QButtonGroup(self)
        sizes = ["Small", "Medium", "Large"]
        self.size_buttons = {}
        size_button_layout = QVBoxLayout()
        for size in sizes:
            btn = QPushButton(size)
            btn.setCheckable(True)
            btn.setFixedSize(100, 100)
            btn.setStyleSheet("font-size: 16px; background-color: #444; color: white;")
            self.size_group.addButton(btn)
            self.size_buttons[size] = btn
            size_button_layout.addWidget(btn)
        self.size_group.buttonClicked.connect(self.size_button_clicked)
        top_section.addLayout(size_button_layout)

        # --- Button Section ---
        button_section = QVBoxLayout()
        #Positioned based on order below
        # Start Button
        # Position: Top of the button section
        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(100, 130)
        self.start_button.setStyleSheet("font-size: 18px; background-color: green; color: white;")
        self.start_button.clicked.connect(self.start_process)
        button_section.addWidget(self.start_button)

        # Motor Settings Button
        # Position: Below the Start button
        self.motor_settings_button = QPushButton("Settings")
        self.motor_settings_button.setFixedSize(100, 60)
        self.motor_settings_button.setStyleSheet("font-size: 14px; background-color: #444; color: white;")
        self.motor_settings_button.clicked.connect(self.open_motor_settings)
        button_section.addWidget(self.motor_settings_button)

        # Recipes Button
        # Position: Below the Exit button
        self.settings_button = QPushButton("Recipes")
        self.settings_button.setFixedSize(100, 60)
        self.settings_button.setStyleSheet("font-size: 14px; background-color: #444; color: white;")
        self.settings_button.clicked.connect(self.open_settings)
        button_section.addWidget(self.settings_button)

        # Exit Button
        # Position: Below the Motor Settings button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setFixedSize(100, 40)
        self.exit_button.setStyleSheet("font-size: 14px; background-color: red; color: white;")
        self.exit_button.clicked.connect(self.close_program)  # Connect to close_program method
        button_section.addWidget(self.exit_button)

        

        # Add the button section to the top section
        top_section.addLayout(button_section)

        # --- Instruction Label ---
        self.instruction_label = QLabel("Configure options and press Start")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet("font-size: 20px; padding: 1px;")

        # --- Next Button ---
        self.next_button = QPushButton("Next")
        self.next_button.setFixedSize(120, 50)
        self.next_button.setStyleSheet("font-size: 16px; background-color: blue; color: white;")
        self.next_button.clicked.connect(self.next_step)
        self.next_button.hide()

        # --- Abort Button ---
        self.abort_button = QPushButton("Abort")
        self.abort_button.setFixedSize(120, 50)
        self.abort_button.setStyleSheet("font-size: 16px; background-color: red; color: white;")
        self.abort_button.clicked.connect(self.abort_process)
        self.abort_button.hide()  # Initially hidden

        # --- Button Row Layout ---
        button_row_layout = QHBoxLayout()
        button_row_layout.addWidget(self.abort_button, alignment=Qt.AlignLeft)  # Add Abort button to the left
        button_row_layout.addStretch()  # Add stretch to push the buttons apart
        button_row_layout.addWidget(self.next_button, alignment=Qt.AlignRight)  # Add Next button to the right

        # --- Add sections to the main layout ---
        main_layout.addLayout(top_section)
        main_layout.addWidget(self.instruction_label)
        main_layout.addLayout(button_row_layout)  # Add the button row layout to the main layout
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_weight)

    def size_button_clicked(self, button):
        for btn in self.size_buttons.values():
            btn.setStyleSheet("font-size: 16px; background-color: #444; color: white;")
        button.setStyleSheet("font-size: 16px; background-color: #888; color: white;")

    def show_interlock_warning(self):
        QMessageBox.warning(self, "Cover Open", "Cover is open – motor stopped for safety. Please close the cover and try again.")

    def start_process(self):
        selected_size = None
        for size, btn in self.size_buttons.items():
            if btn.isChecked():
                selected_size = size
                break
        if selected_size is None:
            self.instruction_label.setText("Please select a size!")
            return

        self.selected_flavor = self.flavor_dropdown.currentText()
        self.selected_size = selected_size
        self.recipe = self.app_settings["sizes"].get(self.selected_flavor, {}).get(self.selected_size, {})
        if not self.recipe:
            self.instruction_label.setText("Recipe not found!")
            return

        self.flavor_dropdown.hide()
        for btn in self.size_buttons.values():
            btn.hide()
        self.start_button.hide()
        self.settings_button.hide()  # Hide the Settings button when the process starts
        self.motor_settings_button.hide()  # Hide the Motor Settings button when the process starts
        self.exit_button.hide()  # Hide the Exit button when the process starts

        self.rotor_speed_label.hide()  # Hide the rotor speed label when the process starts
        self.abort_button.show()  # Show the Abort button when the process starts
        self.motor_stopped = False
        self.state = 1
        self.update_ui_for_state()

    def next_step(self):
        if self.motor.interlock_triggered():
            self.motor.check_interlock_and_stop()
            self.show_interlock_warning()
            return

        if self.state == 1:
            self.instruction_label.setText("Zeroing cup, please wait...")
            QApplication.processEvents()
            current_weight_oz = self.load_cell.get_weight() * GRAMS_TO_OZ  # Get current weight in ounces
            self.load_cell.zero(current_weight_oz)  # Zero the scale based on the current weight
            time.sleep(0.5)
            self.state = 2
            self.instruction_label.setText("Shaving ice... Please wait.")
            if not self.motor.start():
                self.show_interlock_warning()
                return
            self.motor.set_speed(self.app_settings["rotor_speed"])
            self.timer.start()
            self.next_button.hide()
        elif self.state == 2:
            self.timer.stop()
            try:
                self.motor.stop()
            except Exception as e:
                print("[WARNING] Error stopping motor:", e)
            self.instruction_label.setText("Ice shaving complete. Zeroing cup for flavor addition...")
            QApplication.processEvents()
            current_weight_oz = self.load_cell.get_weight() * GRAMS_TO_OZ  # Get current weight in ounces
            self.load_cell.zero(current_weight_oz)  # Zero the scale before adding flavor
            time.sleep(0.5)
            self.state = 3
            self.instruction_label.setText("Add flavor until target weight reached.")
            self.timer.start()
            self.next_button.hide()
        elif self.state == 3:
            self.timer.stop()
            self.state = 4
            self.instruction_label.setText("Flavor addition complete. Blend the cup to finish.")
            self.next_button.setText("Finish")
            self.next_button.show()
            self.exit_button.hide()  # Hide the Exit button during the last stage
        elif self.state == 4:
            self.abort_button.hide()  # Hide the Abort button before showing the Finish button
            self.reset_ui()  # Return to the main page after clicking Finish

    def update_weight(self):
        # Ensure gauge is initialized before updating its value
        if not hasattr(self, 'gauge'):
            self.gauge = GaugeWidget()
            self.gauge.setFixedSize(80, 180)

            # Create a layout for the gauge only
            gauge_layout = QHBoxLayout()
            gauge_layout.addStretch()
            gauge_layout.addWidget(self.gauge)
            gauge_layout.addStretch()

            # Insert the gauge layout into the main layout
            self.layout().insertLayout(2, gauge_layout)

        self.motor.check_interlock_and_stop()
        if self.motor.was_interrupted:
            self.timer.stop()
            self.motor.was_interrupted = False
            self.show_interlock_warning()
            if not self.motor.interlock_triggered():
                self.motor.start()
                self.motor.set_speed(self.app_settings["rotor_speed"])
                self.timer.start()
            return

        weight_grams = self.load_cell.get_weight()
        weight_oz = weight_grams * GRAMS_TO_OZ

        if self.state == 2:
            target = self.recipe.get("Ice", 0)
        elif self.state == 3:
            target = self.recipe.get("Flavor", 0)
        else:
            target = 0

        self.instruction_label.setText(
            f"Current weight: {weight_oz:.2f} oz (Target: {target} oz)"
        )
        self.gauge.setValue(weight_oz, target)

        # Enable or disable the next button based on the target weight
        if (self.state == 2 or self.state == 3) and weight_oz >= target:
            if self.state == 2 and not self.motor_stopped:
                try:
                    self.motor.stop()
                except Exception as e:
                    print("[WARNING] Error stopping motor:", e)
                self.motor_stopped = True
            self.next_button.setEnabled(True)
            self.next_button.show()  # Ensure the button is visible
        elif self.state == 2 or self.state == 3:
            self.next_button.setEnabled(False)
            self.next_button.show()  # Ensure the button is visible

    def update_ui_for_state(self):
        if self.state == 1:
            self.instruction_label.setText("Place your cup and then press Next.")
            self.next_button.setText("Next")
            self.next_button.setEnabled(True)  # Enable the button on the first page
            self.next_button.show()
        elif self.state == 2 or self.state == 3:
            # Add GaugeWidget dynamically during later stages
            if not hasattr(self, 'gauge'):
                self.gauge = GaugeWidget()
                self.gauge.setFixedSize(80, 180)
                gauge_layout = QHBoxLayout()
                gauge_layout.addStretch()
                gauge_layout.addWidget(self.gauge)
                gauge_layout.addStretch()
                self.layout().insertLayout(2, gauge_layout)  # Insert gauge layout dynamically
            self.next_button.setEnabled(False)  # Disable the button initially for target-hitting stages

    def reset_ui(self):
        self.flavor_dropdown.show()
        for btn in self.size_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet("font-size: 16px; background-color: #444; color: white;")
            btn.show()
        self.start_button.show()
        self.next_button.hide()
        self.exit_button.show()  # Show the Exit button again
        self.settings_button.show()  # Show the Settings button again
        self.motor_settings_button.show()  # Show the Motor Settings button again
        self.instruction_label.setText("Configure options and press Start")

        # Remove GaugeWidget if it exists
        if hasattr(self, 'gauge'):
            self.layout().removeWidget(self.gauge)
            self.gauge.deleteLater()
            del self.gauge
        
        self.abort_button.hide()  # Hide the Abort button when resetting the UI
        self.rotor_speed_label.show()  # Show the rotor speed label when returning to the start screen
        self.state = 0
        self.motor_stopped = False

    def close_program(self):
        """Close the application."""
        print("[INFO] Exiting the program...")
        QApplication.quit()

    def open_settings(self):
        """Open the settings UI."""
        if self.settings_window is None:
            self.settings_window = SettingsWindow()
        self.settings_window.show()
        self.settings_window.save_settings = self.reload_settings  # Hook into save_settings

    def open_motor_settings(self):
        """Open the motor settings UI."""
        self.motor_settings_window = WeightDisplay()
        self.motor_settings_window.main_ui_window = self
        self.motor_settings_window.save_motor_speed_callback = self.reload_settings  # Set callback to reload settings
        self.motor_settings_window.show()
        self.hide()

    def reload_settings(self):
        """Reload settings after saving."""
        self.app_settings = settings.load_settings()
        self.flavor_dropdown.clear()
        self.flavor_dropdown.addItems(list(self.app_settings["sizes"].keys()))
        self.rotor_speed_label.setText(f"Rotor Speed Setting: {self.app_settings['rotor_speed']}%")
        print("[INFO] Settings reloaded in MainUI.")

    def abort_process(self):
        """Abort the process, stop the motor, and return to the start page."""
        print("[INFO] Process aborted by user.")
        try:
            self.motor.stop()  # Stop the motor if it's running
        except Exception as e:
            print(f"[WARNING] Error stopping motor during abort: {e}")
        
        # Perform the same cleanup as reset_ui
        self.flavor_dropdown.show()
        for btn in self.size_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet("font-size: 16px; background-color: #444; color: white;")
            btn.show()
        self.start_button.show()
        self.next_button.hide()
        self.exit_button.show()  # Show the Exit button again
        self.settings_button.show()  # Show the Settings button again
        self.motor_settings_button.show()  # Show the Motor Settings button again
        self.instruction_label.setText("Configure options and press Start")

        # Remove GaugeWidget if it exists
        if hasattr(self, 'gauge'):
            self.layout().removeWidget(self.gauge)
            self.gauge.deleteLater()
            del self.gauge

        # Stop the timer for weight updates
        if self.timer.isActive():
            self.timer.stop()

        self.abort_button.hide()  # Hide the Abort button when resetting the UI
        self.rotor_speed_label.show()  # Show the rotor speed label when returning to the start screen
        self.state = 0
        self.motor_stopped = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())
