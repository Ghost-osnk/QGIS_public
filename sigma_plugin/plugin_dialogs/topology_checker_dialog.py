import os
from typing import Union

from qgis.PyQt import uic
from qgis.PyQt import QtGui, QtCore, QtWidgets
import qgis.gui as qgs_qui
from ..help_tools.config_reader import ConfigWorker

topology_checker_ui, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "ui_files/Topology_checker.ui")
)


class TopologyCheckerDialog(QtWidgets.QDialog, topology_checker_ui):

    """PYQT class of Topology checker dialog window"""

    def __init__(
            self,
            iface: qgs_qui.QgisInterface,
            config: ConfigWorker,
            parent=None
    ):
        super().__init__(parent)
        self.iface = iface
        self.setupUi(self)
        # self.installEventFilter(self)
        self.config = config
        self.table_widget = self.tableWidget

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        # Comment this method if qgis crash
        # print(event)
        try:
            for canvas_item in self.iface.mapCanvas().scene().items():
                if isinstance(canvas_item, (qgs_qui.QgsHighlight, qgs_qui.QgsVertexMarker)):
                    self.iface.mapCanvas().scene().removeItem(canvas_item)
        except Exception as e:
            print(e)

    def keyPressEvent(self, key_event: QtGui.QKeyEvent) -> None:
        # Comment this method if qgis crash
        if key_event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()

    def remember_settings(self, autocomplete=False):

        checkbox_objects = list(
            x for x in self.findChildren(QtWidgets.QCheckBox)
        )

        if autocomplete:
            for chb_name, value in self.config.config_reader["remember_settings"].items():
                for checkbox_object in checkbox_objects:
                    if chb_name == checkbox_object.objectName():
                        checkbox_object.setChecked(value)
        else:
            checkbox_settings = {}
            for checkbox in checkbox_objects:
                checkbox_settings[checkbox.objectName()] = checkbox.isChecked()
            self.config.config_writer(
                change_field="remember_settings", new_value=checkbox_settings
            )

    # def eventFilter(
    #         self,
    #         source: QtCore.QObject,
    #         event: Union[QtCore.QEvent, QtGui.QMouseEvent]
    # ) -> bool:
    #
    #     if isinstance(
    #             event, QtGui.QMouseEvent
    #     ) and event.type() == QtCore.QEvent.Type.MouseButtonPress:
    #         if event.button() == QtCore.Qt.MouseButton.RightButton:
    #             context_menu = QtWidgets.QMenu(self.table_widget)
    #             context_menu.addAction(QtWidgets.QAction("test 1", self.table_widget))
    #             context_menu.exec(event.globalPos())
    #             print("sas")
    #
    #     return super().eventFilter(source, event)

