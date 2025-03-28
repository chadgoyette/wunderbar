# --- loadcell_reader_qt.py ---

from PySide6.QtCore import QObject, Signal, Property, QTimer, Slot
from hx711_reader import LoadCell

class LoadCellReader(QObject):
    weightUpdated = Signal(float)
    weightChanged = Signal()
    tareCompleted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sensor = None  # delay actual init
        self._weight = 0.0

        self.init_timer = QTimer(self)
        self.init_timer.setSingleShot(True)
        self.init_timer.timeout.connect(self.delayed_init)
        self.init_timer.start(1500)  # Wait until Qt settles
     

    def initial_tare(self):
        print("[INFO] Initial delayed tare (Python-side)")
        self._sensor.tare()

    def delayed_init(self):
        print("[INFO] LoadCellReader ready for explicit initialization.")
        # Removed automatic initialization here

    @Slot()
    def initialize_sensor(self):
        if self._sensor is None:
            print("[INFO] Initializing LoadCell...")
            self._sensor = LoadCell()
            print("[INFO] LoadCell initialized.")
            # Start polling weight only after explicit initialization
            self.timer = QTimer(self)
            self.timer.setInterval(100)
            self.timer.timeout.connect(self.read_weight)
            self.timer.start()

    def _delayed_tare(self):
        print("[INFO] Initial delayed tare (Python-side)")
        self._sensor.tare()
        self._weight = 0.0
        self.weightChanged.emit()
        self.weightUpdated.emit(0.0)

    def read_weight(self):
        if self._sensor is None:
            print("[ERROR] LoadCell is not initialized!")
            return

        samples = [self._sensor.get_weight() for _ in range(5)]
        avg_weight = sum(samples) / len(samples)

        # Removed raw samples debug log
        if abs(avg_weight - self._weight) > 0.01:
            self._weight = avg_weight
            self.weightUpdated.emit(self._weight)
            self.weightChanged.emit()
        else:
            print("[DEBUG] No significant weight change detected.")

    def get_weight(self):
        samples = [self._sensor.get_weight() for _ in range(5)]
        return sum(samples) / len(samples)

    @Slot()
    def tare(self):
        print("[INFO] Taring from QML...")
        self._sensor.tare()
        self._weight = 0.0
        self.weightChanged.emit()
        self.weightUpdated.emit(0.0)
        print("[INFO] Tare complete — signal emitted to QML")
        self.tareCompleted.emit()  # Ensure this signal is emitted

    @Slot()
    def stop_timer(self):
        print("[INFO] Stopping internal load cell timer")
        self.timer.stop()

    @Slot()
    def start_timer(self):
        print("[INFO] Starting internal load cell timer")
        self.timer.start()

    weight = Property(float, fget=get_weight, notify=weightChanged)