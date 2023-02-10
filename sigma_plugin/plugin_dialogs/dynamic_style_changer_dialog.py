import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets


dynamic_style_changer_ui, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "ui_files/Dynamic_style_changer.ui"))


class DynamicStyleChangerDialog(QtWidgets.QDialog, dynamic_style_changer_ui):
    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
