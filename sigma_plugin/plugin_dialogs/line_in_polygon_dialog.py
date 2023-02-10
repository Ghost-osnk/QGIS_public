import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets


import_data_ui, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "ui_files/Line_in_polygon.ui"))


class LineInPolygonDialog(QtWidgets.QDialog, import_data_ui):
    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        # self.dlg.setWindowFlags(WindowStaysOnTopHint)
        self.hide_stuff()

    def hide_stuff(self):
        self.groupBox_2.hide()
