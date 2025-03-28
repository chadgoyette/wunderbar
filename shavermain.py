import sys
import os
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonType
from PySide6.QtCore import QUrl, QStringListModel, QObject, Slot
from PySide6.QtCore import QObject, Signal, Property, QTimer
from loadcell_reader_qt import LoadCellReader
from hx711_reader import LoadCell  # ✅
from app_state import AppState
from motor_qt import MotorController
import settings




class SettingsManager(QObject):
    def __init__(self, settings_file, settings_dict):
        super().__init__()
        self.settings_file = settings_file
        self.settings_dict = settings_dict

    @Slot(str, str, str, float)
    def updateValue(self, flavor, size, field, value):
        try:
            self.settings_dict["sizes"][flavor][size][field] = value
            with open(self.settings_file, "w") as f:
                json.dump(self.settings_dict, f, indent=4)
            print(f"Saved: {flavor} / {size} / {field} = {value}")
        except KeyError as e:
            print(f"[ERROR] Invalid key: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to save: {e}")

# Qt app setup
app = QApplication(sys.argv)
engine = QQmlApplicationEngine()
# Create the global instance
app_state = AppState()
# Register Constants singleton
qml_path = os.path.abspath("qml/Constants.qml")
qmlRegisterSingletonType(QUrl.fromLocalFile(qml_path), "App", 1, 0, "Constants")

# Load settings and model
settings_file = "settings.json"
app_settings = settings.load_settings()
flavor_model = QStringListModel(list(app_settings["sizes"].keys()))
load_cell_reader = LoadCellReader()  # LoadCellReader is created but not initialized
motor_controller = MotorController()

print("[DEBUG] LoadCellReader and MotorController initialized.")

# Set context properties before loading UI
engine.rootContext().setContextProperty("AppSettings", app_settings)
engine.rootContext().setContextProperty("FlavorModel", flavor_model)
engine.rootContext().setContextProperty("SettingsManager", SettingsManager(settings_file, app_settings))
engine.rootContext().setContextProperty("AppStackView", None)
engine.rootContext().setContextProperty("LoadCellReader", load_cell_reader)
load_cell_reader.tareCompleted.connect(lambda: print("[INFO] Tare completed signal received"))
# Add debug log to confirm connection
print("[DEBUG] Connected tareCompleted signal to QML.")
engine.rootContext().setContextProperty("AppState", app_state)  # Ensure AppState is set
engine.rootContext().setContextProperty("MotorController", motor_controller)

# Load main UI
engine.load(QUrl.fromLocalFile(os.path.abspath("qml/MainApp.qml")))

if not engine.rootObjects():
    sys.exit(-1)

# Get root and locate the stack view
root = engine.rootObjects()[0]
stack_view = root.findChild(QObject, "stepStack")
if stack_view:
    print("[DEBUG] StackView located successfully.")
else:
    print("[ERROR] StackView not found!")

if app_state:
    print("[DEBUG] AppState initialized successfully.")
else:
    print("[ERROR] AppState is null!")

engine.rootContext().setContextProperty("AppStackView", stack_view)  # Replace placeholder

root.showFullScreen()
sys.exit(app.exec())
