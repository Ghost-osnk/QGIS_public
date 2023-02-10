from typing import List, Dict, Union, Optional

import qgis.gui as qgs_gui
import qgis.core as qgs_core

from ..plugin_dialogs.kv_net_dialog import KvNetDialog
from ..help_tools.config_reader import ConfigWorker
from ..help_tools.help_func import validate_db_and_project_path


class KvNetTool:

    def __init__(self, iface: qgs_gui.QgisInterface, parent_window):

        self.iface = iface
        self.qgis_project = qgs_core.QgsProject().instance()
        self.project_source = ()
        self.kv_net_dlg = KvNetDialog(parent=parent_window)
        self.quarters_for_kv_net = None
        self.config = ConfigWorker(header="kv_net_config")

    def get_kv_net_feature_union(self) -> Dict[tuple, List[qgs_core.QgsGeometry]]:

        project_database_path = self.kv_net_dlg.KvNetDBcomboBox.currentText()
        layer_from_uri = self.config.get_config_file["plugin_configs"]["layers"]["2"]
        layer_from = qgs_core.QgsVectorLayer(
            f"{project_database_path}|{layer_from_uri}",
            layer_from_uri.split("=")[1],
            "ogr"
        )

        progress_bar = self.kv_net_dlg.progressBar
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(layer_from.featureCount())
        progress_bar.show()

        result_feature_union = {}

        for num, feature in enumerate(layer_from.getFeatures()):

            feature_attributes = tuple(
                feature.attributes()[attr_ind] if feature.attributes()[attr_ind] != qgs_core.NULL
                else 0 for attr_ind in
                (feature.fieldNameIndex(feat_name) for feat_name in self.config.config_reader["kv_net_attributes"])
            )
            if feature.hasGeometry() and feature.geometry().isGeosValid() and not feature.geometry().validateGeometry():
                result_feature_union.setdefault(feature_attributes, []).append(feature.geometry())
                progress_bar.setValue(num + 1)

            else:
                geometry_error = feature.geometry().validateGeometry()
                user_message = (
                    "Произошла ошибка при подготовке данных.\n"
                    "Невалидная геометрия, проверьте геометрию.\n"
                    f"Feature_id: {feature.id()}, Error: {geometry_error}\n"
                )
                self.make_statistic(error_message=user_message)
                raise ValueError
            progress_bar.hide()
        return result_feature_union

    @staticmethod
    def merge_geometry(
            kv_net: Dict[tuple, List[qgs_core.QgsGeometry]]
    ) -> Dict[tuple, qgs_core.QgsGeometry]:

        result = {}

        for f_attr, f_geom in kv_net.items():
            geometry = qgs_core.QgsGeometry().fromWkt("GEOMETRYCOLLECTION()")

            for geom in f_geom:
                if geom.isGeosValid():
                    error = geom.validateGeometry()
                    if not error:
                        geometry = geometry.combine(
                            qgs_core.QgsGeometry().fromWkt(geom.asWkt())
                        )
            result[f_attr] = geometry
        return result

    def add_object_in_target_layer(
            self, merged_geometry_feature: Dict[tuple, qgs_core.QgsGeometry]
    ):
        project_database_path = self.kv_net_dlg.KvNetDBcomboBox.currentText()

        layer_from_uri = self.config.get_config_file["plugin_configs"]["layers"]["3"]
        layer_in = qgs_core.QgsVectorLayer(
            f"{project_database_path}|{layer_from_uri}",
            layer_from_uri.split("=")[1],
            "ogr"
        )
        layer_in.startEditing()

        for feature in layer_in.getFeatures():
            layer_in.deleteFeature(feature.id())

        layer_in.commitChanges(stopEditing=False)

        feature_count = 1
        layer_fields = layer_in.fields()

        for f_attr, f_geom in merged_geometry_feature.items():

            new_feature = qgs_core.QgsFeature(layer_fields)
            new_feature.setGeometry(f_geom)
            f_attrs = [
                feature_count, *f_attr, *[qgs_core.NULL] * (len(layer_fields) - len(f_attr) - 1)
            ]
            new_feature.setAttributes(f_attrs)
            layer_in.dataProvider().addFeature(
                new_feature, flags=qgs_core.QgsFeatureSink.Flag.FastInsert
            )
            feature_count += 1

        if layer_in.commitChanges(stopEditing=True):
            user_message = self.config.config_reader["user_messages"]["successful_write"]
            self.iface.messageBar().pushMessage(
                user_message, level=qgs_core.Qgis.MessageLevel.Success, duration=7
            )
            self.qgis_project.reloadAllLayers()
            self.make_statistic(
                kv_count=len(merged_geometry_feature.items()), kv_make=feature_count - 1
            )

        else:
            user_message = " ".join(layer_in.commitErrors())
            self.iface.messageBar().pushMessage(
                user_message, level=qgs_core.Qgis.MessageLevel.Critical, duration=7
            )
            layer_in.rollBack()

    def make_statistic(
            self,
            error_message: Optional[str] = None,
            kv_count: Optional[Union[int, None]] = None,
            kv_make: Optional[Union[int, None]] = None,
    ) -> None:

        template = self.config.config_reader["user_messages"]["result_tab"]
        if kv_count and kv_make:
            result = (
                f"{template['kv_count']} {kv_count}\n"
                f"{template['kv_make']} {kv_make}\n"
                "\n"
                f"{template['delimiter'] * 20}\n"
            )
        else:
            result = (
                f"{error_message}"
                "\n"
                f"{template['delimiter'] * 20}\n"
            )
        self.kv_net_dlg.tabWidget.setCurrentIndex(1)
        self.kv_net_dlg.textResult.insertPlainText(result)

    def make_kv_net(self):
        try:
            self.quarters_for_kv_net = self.get_kv_net_feature_union()
            merged_geometry_features = self.merge_geometry(self.quarters_for_kv_net)
            self.add_object_in_target_layer(merged_geometry_features)

        except (KeyError, ValueError):
            return None

    def kv_net_run(self):
        self.kv_net_dlg.progressBar.hide()
        self.kv_net_dlg.activateWindow()

        if not validate_db_and_project_path(
                qgis_project=self.qgis_project,
                dialog=self.kv_net_dlg,
                iface=self.iface,
                db_combobox=self.kv_net_dlg.KvNetDBcomboBox
        ):
            return

        self.kv_net_dlg.KvNetCanceleButton.clicked.connect(self.kv_net_dlg.close)
        self.kv_net_dlg.KvNetButton.clicked.connect(self.make_kv_net)

        self.kv_net_dlg.exec()
