import os

from qgis.PyQt import uic
from PyQt5.QtCore import Qt, QDataStream
from PyQt5 import QtWidgets, QtNetwork


kv_net_ui, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "plugin_dialogs/ui_files/external_program.ui"))


class MyClient:
    pass


class ExternalProgramDialog(QtWidgets.QDialog, kv_net_ui):
    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)


class ExternalProgram:

    def __init__(self, iface):
        self.iface = iface
        self.external_program_dlg = ExternalProgramDialog()

    def backend(self):
        sk = MyClient()
        sk.send_message(self.external_program_dlg.lineEdit.text())

    def external_program_run(self):
        self.external_program_dlg.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.external_program_dlg.show()
        self.external_program_dlg.pushButton.clicked.connect(self.backend)
        self.external_program_dlg.exec_()

