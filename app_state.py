# app_state.py
from PySide6.QtCore import QObject, Signal, Property

class AppState(QObject):
    def __init__(self):
        super().__init__()
        self._selectedSize = ""
        self._selectedFlavor = ""

    # Signal and property for selectedSize
    selectedSizeChanged = Signal()

    def getSelectedSize(self):
        return self._selectedSize

    def setSelectedSize(self, value):
        if self._selectedSize != value:
            self._selectedSize = value
            self.selectedSizeChanged.emit()

    selectedSize = Property(str, getSelectedSize, setSelectedSize, notify=selectedSizeChanged)

    # Signal and property for selectedFlavor
    selectedFlavorChanged = Signal()

    def getSelectedFlavor(self):
        return self._selectedFlavor

    def setSelectedFlavor(self, value):
        if self._selectedFlavor != value:
            self._selectedFlavor = value
            self.selectedFlavorChanged.emit()

    selectedFlavor = Property(str, getSelectedFlavor, setSelectedFlavor, notify=selectedFlavorChanged)
