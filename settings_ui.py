#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, 
    QComboBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt
import settings

class SettingsWindow(QWidget):
    def __init__(self):
        """Initialize the settings window UI."""
        super().__init__()

        # Load settings from storage
        self.app_settings = settings.load_settings()

        # Configure main window properties
        self.setWindowTitle("Recipe Config")
        self.setFixedSize(725, 400)  # Smaller fixed size to fit on 800x480
        self.setStyleSheet("background-color: black; color: white;")

        # Layout for the settings UI
        layout = QVBoxLayout()
        layout.setSpacing(5)

        # --- Flavor Selection ---
        flavor_layout = QGridLayout()
        flavor_label = QLabel("Select Flavor:")
        flavor_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.flavor_dropdown = QComboBox()
        # Populate dropdown with keys from settings.json
        self.flavor_dropdown.addItems(list(self.app_settings["sizes"].keys()))
        self.flavor_dropdown.setFixedSize(300, 60)
        self.flavor_dropdown.setStyleSheet(
            "font-size: 25px; padding: 5px; background-color: #444; color: white;"
        )
        self.flavor_dropdown.currentIndexChanged.connect(self.load_flavor_settings)

        flavor_layout.addWidget(self.flavor_dropdown, 0, 0, Qt.AlignCenter)
        layout.addLayout(flavor_layout)

        # --- Size Headers ---
        size_layout = QGridLayout()
        size_layout.setHorizontalSpacing(0)
        size_labels = ["Small", "Medium", "Large"]
        
        for col, size in enumerate(size_labels, start=1):
            label = QLabel(size)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 16px; font-weight: bold;")
            size_layout.addWidget(label, 0, col)

        # --- Ingredient Labels and Input Fields ---
        self.ingredients = ["Flavor", "Yogurt", "Ice"]
        self.spin_boxes = {}  # Dictionary to store spin boxes for easy access

        for row, ingredient in enumerate(self.ingredients, start=1):
            # Add ingredient labels on the left
            ingredient_label = QLabel(ingredient)
            ingredient_label.setStyleSheet("font-size: 20px; font-weight: bold;")
            size_layout.addWidget(ingredient_label, row, 0)

            # Add input fields with up/down arrows for each size
            for col, size in enumerate(size_labels, start=1):
                spin_box = QDoubleSpinBox()
                spin_box.setSingleStep(0.01)
                spin_box.setDecimals(2)
                spin_box.setMinimum(0.0)
                spin_box.setMaximum(50.0)
                spin_box.setFixedSize(200, 80)  # Reduced size
                spin_box.setStyleSheet(
                    """
                    QDoubleSpinBox {
                        font-size: 28px; 
                        padding: 3px; 
                        border: 2px solid white;
                        background-color: #222; 
                        color: white;
                    }
                    QDoubleSpinBox::up-button {
                        width: 100px; 
                        height: 40px;
                    }
                    QDoubleSpinBox::down-button {
                        width: 100px; 
                        height: 40px;
                    }
                    """
                )
                key = f"{size}_{ingredient}"
                self.spin_boxes[key] = spin_box
                size_layout.addWidget(spin_box, row, col)

        layout.addLayout(size_layout)

        # --- Save and Close Buttons ---
        button_layout = QGridLayout()
        
        save_button = QPushButton("Save")
        save_button.setFixedSize(120, 50)
        save_button.setStyleSheet("font-size: 16px; background-color: blue; color: white;")
        save_button.clicked.connect(self.save_settings)
        
        close_button = QPushButton("Close")
        close_button.setFixedSize(120, 50)
        close_button.setStyleSheet("font-size: 16px; background-color: red; color: white;")
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(save_button, 0, 0)
        button_layout.addWidget(close_button, 0, 1)
        layout.addLayout(button_layout)

        # Set the final layout
        self.setLayout(layout)

        # Load initial settings for the default flavor
        self.load_flavor_settings()

    def load_flavor_settings(self):
        """Load the ingredient values for the selected flavor."""
        selected_flavor = self.flavor_dropdown.currentText()
        flavor_recipe = self.app_settings["sizes"].get(selected_flavor, {})
        for size in ["Small", "Medium", "Large"]:
            size_values = flavor_recipe.get(size, {})
            for ingredient in self.ingredients:
                key = f"{size}_{ingredient}"
                value = size_values.get(ingredient, 0.0)
                self.spin_boxes[key].setValue(value)

    def save_settings(self):
        """Save the ingredient values for the selected flavor."""
        selected_flavor = self.flavor_dropdown.currentText()
        if selected_flavor not in self.app_settings["sizes"]:
            self.app_settings["sizes"][selected_flavor] = {}
        for size in ["Small", "Medium", "Large"]:
            if size not in self.app_settings["sizes"][selected_flavor]:
                self.app_settings["sizes"][selected_flavor][size] = {}
            for ingredient in self.ingredients:
                key = f"{size}_{ingredient}"
                self.app_settings["sizes"][selected_flavor][size][ingredient] = self.spin_boxes[key].value()

        # Save settings to file
        settings.save_settings(self.app_settings)
        print(f"[INFO] Saved settings for {selected_flavor}.")
        if hasattr(self, 'save_settings_callback'):
            self.save_settings_callback()  # Trigger callback to reload settings

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec_())
