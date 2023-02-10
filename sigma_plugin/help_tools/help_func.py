import os
from typing import List, Union

from dataclasses import dataclass
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtWidgets import QComboBox, QDialog

import qgis.core as qgs_core
import qgis.gui as qgs_gui

from .config_reader import ConfigWorker


def validate_db_and_project_path(
        qgis_project: qgs_core.QgsProject,
        dialog: QDialog,
        iface: qgs_gui.QgisInterface,
        db_combobox: QComboBox = None,
) -> bool:
    user_message = ConfigWorker(header="plugin_configs").config_reader[
        "user_messages"
    ]
    if qgis_project.absoluteFilePath() == "":
        dialog.close()
        iface.messageBar().pushMessage(
            user_message["project_missing"],
            level=qgs_core.Qgis.MessageLevel.Critical,
            duration=10
        )
        return False
    if not _get_available_dbs_in_project(
        db_combobox=db_combobox,
        qgis_project=qgis_project,
        iface=iface,
        user_message=user_message["db_version_failed"]
    ):
        return False
    return True


def _get_available_dbs_in_project(
        db_combobox: QComboBox,
        qgis_project: qgs_core.QgsProject,
        iface: qgs_gui.QgisInterface,
        user_message: str
) -> bool:
    dbs_path = _get_available_dbs_path(qgis_project=qgis_project)
    if dbs_path and db_combobox is not None:
        db_combobox.clear()
        for path in dbs_path:
            db_combobox.addItem(path)
        return True
    elif dbs_path and db_combobox is None:
        return True
    else:
        iface.messageBar().pushMessage(
            user_message, level=qgs_core.Qgis.MessageLevel.Warning, duration=3
        )
        return False


def translate(message: str) -> str:
    plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    locale = QSettings().value("locale/userLocale")[0:2]
    locale_path = os.path.join(
        plugin_dir,
        "i18n",
        f"Sigma_{locale}.qm"
    )

    if os.path.exists(locale_path):
        translator = QTranslator()
        translator.load(locale_path)
        QCoreApplication.installTranslator(translator)

    return QCoreApplication.translate("Sigma", message)


def _check_db_version(db_source: str) -> bool:
    layer_features = qgs_core.QgsVectorLayer(f"{db_source}|layername=sys_info", "sys_inf_l", "ogr")
    feature_request = qgs_core.QgsFeatureRequest().setFilterExpression(
        '"property"=\'database_version\''
    )
    result = layer_features.getFeatures(feature_request)

    try:
        return bool(int(next(result)["value"]) >= 2)
    except StopIteration:
        return False


def _get_available_dbs_path(qgis_project: qgs_core.QgsProject) -> List[str]:
    all_project_db = list(obj_layer for obj_layer in qgis_project.mapLayers().values())
    project_database = {
        layer.publicSource().split("|")[0] for layer in all_project_db if
        layer.publicSource().split("|")[0].endswith(".gpkg")
    }
    available_dbs = [path for path in project_database if _check_db_version(db_source=path)]

    return available_dbs


def get_geometry_layer_from_db(
        db_combobox: QComboBox,
        qgis_project: qgs_core.QgsProject,
        geom_type: [int, None] = None,
        layer_name: [str, None] = None
) -> qgs_core.QgsVectorLayer:
    current_layers: Union[list[qgs_core.QgsVectorLayer], list[qgs_core.QgsMapLayer], None] = None
    if geom_type:
        layer_type = ConfigWorker(header="plugin_configs").config_reader["layers"]

        current_layers = qgis_project.mapLayersByName(
            layer_type[str(geom_type)].split("=")[1]
        )

    if layer_name:
        current_layers = qgis_project.mapLayersByName(
            layer_name
        )
        if not current_layers:
            current_layers: list[qgs_core.QgsVectorLayer] = [
                qgs_core.QgsVectorLayer(
                    f"{db_combobox.currentText()}|layername={layer_name}", f"{layer_name}", "ogr"
                )
            ]
    for current_layer in current_layers:
        if current_layer.publicSource().split("|")[0] == db_combobox.currentText():
            return current_layer
        if current_layer.isValid() and current_layer.isTemporary():
            return current_layer
        else:
            raise ValueError


@dataclass
class TopologyFeatureData:
    """Topology Error dataclass"""

    layer_name: str = ""
    feature_id: str = ""
    error_type: str = ""
    feature_object: Union[qgs_core.QgsFeature, List[qgs_core.QgsFeature]] = None
    highlight: Union[qgs_gui.QgsHighlight, List[qgs_gui.QgsHighlight], None] = None
    error_coordinate: Union[
        Union[qgs_core.QgsGeometry, qgs_core.QgsPointXY],
        List[Union[qgs_core.QgsGeometry, qgs_core.QgsPointXY]], None
    ] = None
    meaning: str = ""
    error_fixing: str = ""

    @property
    def get_field_names_for_insert(self) -> tuple[str, ...]:
        return "layer_name", "feature_id", "error_type", "meaning", "error_fixing"


@dataclass
class TopologyFixingData:
    layer_name: str
    error_type: Union[str, int]
    feature_object: qgs_core.QgsFeature
    status: bool
    description: str = ""


@dataclass
class LineToPolygonData:
    """Documentation for lineToPolyData class"""

    line_features: List[qgs_core.QgsFeature] = None
    polygon_features: List[qgs_core.QgsFeature] = None
    quarters_features: List[qgs_core.QgsFeature] = None
    buffers_size: List[float] = None
