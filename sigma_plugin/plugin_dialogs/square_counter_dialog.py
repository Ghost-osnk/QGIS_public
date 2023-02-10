import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets


square_counter_ui, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "ui_files/Square_counter.ui"))


class SquareCounterDialog(QtWidgets.QDialog, square_counter_ui):
    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
