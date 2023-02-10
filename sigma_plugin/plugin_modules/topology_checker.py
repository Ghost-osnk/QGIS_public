from typing import List

from PyQt5.QtCore import Qt

from qgis.PyQt import QtWidgets
from qgis import core, gui

from ..plugin_dialogs.topology_checker_dialog import TopologyCheckerDialog
from ..help_tools.config_reader import ConfigWorker
from ..help_tools.help_func import validate_db_and_project_path, get_geometry_layer_from_db, LineToPolygonData
from ..plugin_dialogs.dialog_tools.topology_checker_ui_worker import TopologyCheckerUiWorker
from .check_module.dr_check.dr_geometry_check import DRGeometryCheck, GeometryCheckType
from .check_module.dr_check.dr_intersection_line_check import DRIntersectionLine


class TopologyCheckerTool:
    """Class for topology and geometry checking."""

    def __init__(self, iface):

        self.iface: gui.QgisInterface = iface
        self.qgis_project = core.QgsProject().instance()
        self.config = ConfigWorker(header="topology_checker_config")
        self.topology_checker_dlg = TopologyCheckerDialog(
            iface=self.iface,
            config=self.config
        )
        self.errors_features_list = []
        self.table_delegator = TopologyCheckerUiWorker(
            table_widget=self.topology_checker_dlg.tableWidget,
            errors_list=self.errors_features_list,
            iface=self.iface,
            config=self.config,
            db_combobox=self.topology_checker_dlg.TopologyCheckerDBcomboBox
        )
        self.layers_for_check: list[core.QgsVectorLayer, ...] = []

    def _get_layers_for_check(self) -> None:
        self.layers_for_check.extend([
            get_geometry_layer_from_db(
                qgis_project=self.qgis_project,
                geom_type=1,
                db_combobox=self.topology_checker_dlg.TopologyCheckerDBcomboBox
            ),
            get_geometry_layer_from_db(
                qgis_project=self.qgis_project,
                geom_type=2,
                db_combobox=self.topology_checker_dlg.TopologyCheckerDBcomboBox
            )
        ])

    def check_geometry(self, check_type: List[GeometryCheckType]):
        current_db = self.topology_checker_dlg.TopologyCheckerDBcomboBox.currentText()

        if current_db.endswith(".gpkg"):
            checker = DRGeometryCheck(
                layers_for_check=self.layers_for_check,
                config=self.config,
                progress_bar=self.topology_checker_dlg.progressBar
            )

            if check_type:
                self.errors_features_list.extend(checker.run_check(check_types=check_type))

        else:
            # TODO for other base
            pass

    def result_backend(self):

        self.table_delegator.refresh_table_and_errors()
        self.topology_checker_dlg.tabWidget.setCurrentIndex(1)
        check_types = []

        for check_box in self.topology_checker_dlg.findChildren(QtWidgets.QCheckBox):
            if check_box.isChecked() and check_box.parent().objectName() in (
                    "attrCheckBox", "geomCheckBox", "groupBox"
            ):
                if check_box.objectName() == "checkIntersectionLine":
                    self.find_line()
                else:
                    check_types.append(getattr(GeometryCheckType, f"{check_box.objectName()}"))

        self.check_geometry(check_type=check_types)
        self.table_delegator.insert_errors_data_in_table()
        self.topology_checker_dlg.remember_settings()

    def find_line(self):
        line_worker: DRIntersectionLine = DRIntersectionLine()
        line_layer: core.QgsVectorLayer = self.layers_for_check[0]
        layers_feature_data: list[tuple] = [
            (feat, feat.id(), feat.geometry()) for feat in line_layer.getFeatures()
        ]
        mem_polygon_layer: core.QgsVectorLayer = get_geometry_layer_from_db(
            qgis_project=self.qgis_project,
            db_combobox=self.topology_checker_dlg.TopologyCheckerDBcomboBox,
            layer_name="Buffered_lines"
        )
        polygon_data: LineToPolygonData = LineToPolygonData(
            layer_name=mem_polygon_layer.name(),
            polygon_features=list(feat for feat in mem_polygon_layer.getFeatures())
        )
        if not mem_polygon_layer.isValid():
            self.iface.messageBar().pushMessage(
                "Нет слоя с преобразованными линиями.",
                core.Qgis.MessageLevel.Warning,
                duration=3
            )
            return
        self.errors_features_list.extend(
            line_worker.run_check(
                layer_name=line_layer.name(),
                features=[data[0] for data in layers_feature_data],
                feature_ids=[data[1] for data in layers_feature_data],
                feature_geoms=[data[2] for data in layers_feature_data],
                optional_param=polygon_data
            )
        )

    def topology_checker_run(self):

        if not validate_db_and_project_path(
                qgis_project=self.qgis_project,
                dialog=self.topology_checker_dlg,
                db_combobox=self.topology_checker_dlg.TopologyCheckerDBcomboBox,
                iface=self.iface
        ):
            return
        self._get_layers_for_check()
        self.topology_checker_dlg.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.topology_checker_dlg.progressBar.hide()
        self.topology_checker_dlg.groupBox_4.hide()
        self.topology_checker_dlg.groupBox_5.hide()

        self.topology_checker_dlg.show()
        self.topology_checker_dlg.remember_settings(autocomplete=True)

        self.topology_checker_dlg.TopologyCheckButton.clicked.connect(
            self.result_backend
        )
        self.topology_checker_dlg.TopologyCheckCanceleButton.clicked.connect(
            self.topology_checker_dlg.close
        )
        self.topology_checker_dlg.tableWidget.cellDoubleClicked.connect(
            self.table_delegator.make_highlights
        )
        self.topology_checker_dlg.tableWidget.customContextMenuRequested.connect(
            self.table_delegator.run_table_menu
        )
        self.topology_checker_dlg.exec_()
