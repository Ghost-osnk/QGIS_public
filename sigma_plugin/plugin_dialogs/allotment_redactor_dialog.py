import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets


kv_net_ui, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "ui_files/Allotment_redactor.ui"))


class AllotmentRedactorDialog(QtWidgets.QDialog, kv_net_ui):
    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
