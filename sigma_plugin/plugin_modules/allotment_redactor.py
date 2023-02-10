from qgis import core, gui
from PyQt5 import QtCore, QtWidgets
from PyQt5 import QtNetwork

from ..plugin_dialogs.allotment_redactor_dialog import AllotmentRedactorDialog
from ..help_tools.config_reader import ConfigWorker
from ..help_tools.help_func import validate_db_and_project_path, get_geometry_layer_from_db


class MyServer:

    pass


class AllotmentRedactorTool:
    """Import data class for Sigma plugin"""

    def __init__(self, iface):
        self.iface: gui.QgisInterface = iface
        self.qgis_project = core.QgsProject().instance()
        self.allotment_redactor_dlg = AllotmentRedactorDialog()
        # self.config = ConfigWorker(header="import_data_config")

    def get_current_layer(self):
        current_layer: core.QgsVectorLayer = get_geometry_layer_from_db(
            db_combobox=self.allotment_redactor_dlg.DBcomboBox,
            qgis_project=self.qgis_project,
            geom_type=2,
        )
        return current_layer

    def backend(self):
        current_layer = self.get_current_layer()

        if current_layer.featureAdded.connect(self.a):
            pass
        if current_layer.featureDeleted.connect(self.d):
            pass
        if current_layer.geometryChanged.connect(self.c):
            pass
        if current_layer.attributeAdded.connect(self.aa):
            pass
        if current_layer.attributeDeleted.connect(self.ad):
            pass
        if current_layer.attributeValueChanged.connect(self.avc):
            pass

    def a(self, *args, **kwargs):
        print(args, kwargs)
        print("Feature_added")

    def d(self, *args, **kwargs):
        print(args, kwargs)
        print("Feature_deleted")

    def c(self, *args, **kwargs):
        print(args, kwargs)
        print("Feature_changed")

    def aa(self, *args, **kwargs):
        print(args, kwargs)
        print("Feature_added_attr")

    def ad(self, *args, **kwargs):
        print(args, kwargs)
        print("Feature_deleted_attr")

    def avc(self, *args, **kwargs):
        print(args, kwargs)
        print("Feature_attr_value_changed")

    def sos(self, *args, **kwargs):
        print(*args, **kwargs)
        print("Signal")

    def test(self):
        test_layer: core.QgsVectorLayer = self.iface.activeLayer()
        f = next(test_layer.getFeatures())
        # test_layer.beforeEditingStarted.connect(self.sos)
        # app: core.QgsApplication = core.QgsApplication.instance()

        f_form: gui.QgsAttributeDialog = self.iface.getFeatureForm(test_layer, f)


        # self.iface.openFeatureForm(test_layer, f)

        # "featureactiondlg"
        # for wid in app.allWidgets():
        #     if "geo" in wid.objectName():
        #         print(wid.windowTitle())
        #         print(wid.objectName())
        # print(attrTables)
        # for x in attrTables:
        #     w_title = x.windowTitle()
        #     tab_lyr = w_title[:w_title.index("::") - 1]
        #     print(w_title, tab_lyr)

    def allotment_redactor_data_run(self):
        if not validate_db_and_project_path(
                qgis_project=self.qgis_project,
                dialog=self.allotment_redactor_dlg,
                db_combobox=self.allotment_redactor_dlg.DBcomboBox,
                iface=self.iface
        ):
            return

        self.allotment_redactor_dlg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.allotment_redactor_dlg.show()
        self.test()
        self.backend()
        self.allotment_redactor_dlg.exec_()
