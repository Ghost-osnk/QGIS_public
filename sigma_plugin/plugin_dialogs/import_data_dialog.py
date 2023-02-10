import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets


import_data_ui, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "ui_files/Import_data.ui"))


class ImportDataDialog(QtWidgets.QDialog, import_data_ui):
    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        # self.dlg.setWindowFlags(WindowStaysOnTopHint)
