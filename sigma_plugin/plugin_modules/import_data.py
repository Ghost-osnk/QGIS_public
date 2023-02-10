import qgis.core

from ..plugin_dialogs.import_data_dialog import ImportDataDialog
from ..plugin_dialogs.dialog_tools.import_data_ui_worker import ImportDataUiWorker
from ..help_tools.config_reader import ConfigWorker
from ..help_tools.help_func import validate_db_and_project_path, get_geometry_layer_from_db


class ImportDataTool:
    """Import data class for Sigma plugin"""

    def __init__(self, iface, parent_window):

        self.iface = iface
        self.qgis_project = qgis.core.QgsProject().instance()
        self.import_data_dlg = ImportDataDialog(parent=parent_window)
        self.autocomplete_table_data = True
        self.config = ConfigWorker(header="import_data_config")
        self.ui_worker = ImportDataUiWorker(
            import_data_dialog=self.import_data_dlg,
            qgis_interface=self.iface,
            config=self.config
        )

    def make_statistic(
            self,
            cur_feat_count_bf: int,
            imp_feat_count: int,
            imported_feat: int,
            cur_feat_count_af: int,
            null_geometry: int
    ):
        self.import_data_dlg.tabWidget.setCurrentIndex(1)
        template = self.config.config_reader["user_messages"]["result_tab"]
        result = (
            f"{template['cur_feat']} {cur_feat_count_bf}\n"
            f"{template['imp_feat']} {imp_feat_count}\n"
            f"{template['imported']} {imported_feat}\n"
            f"{template['total']} {cur_feat_count_af}\n"
            f"{template['null_geometry']} {null_geometry}\n"
            "\n"
            f"{template['delimiter'] * 20}\n"
        )
        self.import_data_dlg.textResult.insertPlainText(result)

    def _get_crs(self, current_imp_sublayer: qgis.core.QgsVectorLayer):
        unknown_crs = qgis.core.QgsCoordinateReferenceSystem("invalid")
        user_crs = self.import_data_dlg.crsSelector.crs()
        current_imp_sublayer_crs = current_imp_sublayer.crs()
        tr_expression = qgis.core.QgsCoordinateTransform(
            current_imp_sublayer_crs, user_crs, self.qgis_project
        )
        return tuple([user_crs, current_imp_sublayer_crs, unknown_crs, tr_expression])

    def _get_new_feature(
            self,
            f_id: int,
            imported_feature: qgis.core.QgsFeature,
            current_sublayer: qgis.core.QgsVectorLayer,
            field_names_and_values_data: dict[str, list],
            crs: tuple
    ) -> qgis.core.QgsFeature:

        cur_sublayer_field_names = [x.name() for x in current_sublayer.fields()]
        new_feature = qgis.core.QgsFeature(current_sublayer.fields())

        if crs[1] in (crs[2], current_sublayer.crs()):
            new_feature.setGeometry(imported_feature.geometry())
        else:
            new_geometry = qgis.core.QgsGeometry(imported_feature.geometry())
            new_geometry.transform(crs[3])
            new_feature.setGeometry(new_geometry)

        new_feature = self._set_feature_fields(
            f_id=f_id,
            new_feature=new_feature,
            cur_sublayer_field_names=cur_sublayer_field_names,
            field_names_and_values_data=field_names_and_values_data,
            imported_feature=imported_feature,
        )
        return new_feature

    @staticmethod
    def _set_feature_fields(
            f_id: int,
            new_feature: qgis.core.QgsFeature,
            cur_sublayer_field_names: list[str],
            field_names_and_values_data: dict[str, list],
            imported_feature: qgis.core.QgsFeature
    ) -> qgis.core.QgsFeature:
        # maybe replace with setAttributes
        for field_name in cur_sublayer_field_names:
            if field_name == "fid":
                new_feature[field_name] = f_id
            elif field_name in field_names_and_values_data:
                values_for_feature: list[str] = field_names_and_values_data[field_name]
                if field_name == "object_id":
                    new_feature[field_name] = (
                        values_for_feature[0]
                        if isinstance(values_for_feature[0], int)
                        else values_for_feature[1]
                    )
                elif values_for_feature[0] and isinstance(
                        imported_feature[values_for_feature[0]], (int, float)
                ):
                    new_feature[field_name] = imported_feature[values_for_feature[0]]
                else:
                    new_feature[field_name] = int(values_for_feature[1])
            else:
                new_feature[field_name] = 0
        return new_feature

    def _check_ui_data_before_importing(self):
        if not self.import_data_dlg.ImportFileLayerscomboBox.currentText():
            self.iface.messageBar().pushMessage(
                self.config.config_reader["user_messages"]["warning_message_3"],
                level=qgis.core.Qgis.MessageLevel.Critical,
                duration=3
            )
            return False
        if not self.import_data_dlg.ImportFileForestObjIdcomboBox.currentText():

            self.iface.messageBar().pushMessage(
                self.config.config_reader["user_messages"]["warning_message_7"],
                level=qgis.core.Qgis.MessageLevel.Warning,
                duration=3
            )
            return False
        return True

    def importing_data(
            self,
            # a
    ):
        if not self._check_ui_data_before_importing():
            return
        table_rows_values: dict = self.ui_worker.get_table_widget_values()
        import_columns = self.config.config_reader["import_columns"]
        merged_field_names_and_values = {
            filed_name: table_rows_values[
                import_columns[filed_name]
            ] for filed_name in import_columns
        }
        cur_imp_sublayer_name = self.import_data_dlg.ImportFileLayerscomboBox.currentText()
        cur_imp_sublayer = self.ui_worker.import_sub_layers[cur_imp_sublayer_name]

        coordinate_transform = self._get_crs(current_imp_sublayer=cur_imp_sublayer)

        cur_sublayer = get_geometry_layer_from_db(
            db_combobox=self.import_data_dlg.ImportFileDBcomboBox,
            qgis_project=self.qgis_project,
            geom_type=cur_imp_sublayer.geometryType()
        )
        try:
            max_id = max({f.id() for f in cur_sublayer.getFeatures()})
        except ValueError:
            max_id = 0

        imp_feature_count = cur_imp_sublayer.featureCount()
        cur_feature_count = cur_sublayer.featureCount()

        cur_sublayer_dp = cur_sublayer.dataProvider()

        cur_sublayer.startEditing()
        cur_sublayer.setCrs(coordinate_transform[0])

        self.qgis_project.setCrs(coordinate_transform[0])

        progress_bar = self.import_data_dlg.progressBar
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(imp_feature_count)
        progress_bar.show()

        null_geometry_feature_count = 0
        imported_feature_count = 0

        new_features = []

        for count, feat in enumerate(cur_imp_sublayer.getFeatures()):
            progress_bar.setValue(count + 1)
            f_id = max_id + (count + 1)

            new_features.append(
                self._get_new_feature(
                    f_id=f_id,
                    imported_feature=feat,
                    current_sublayer=cur_sublayer,
                    field_names_and_values_data=merged_field_names_and_values,
                    crs=coordinate_transform
                )
            )

            null_geometry_feature_count += 1 if feat.geometry().isNull() else 0
            imported_feature_count += 1

        cur_sublayer_dp.addFeatures(new_features)
        cur_sublayer.commitChanges(stopEditing=True)

        self.qgis_project.reloadAllLayers()
        cur_sublayer.updateExtents()
        self.iface.mapCanvas().setExtent(cur_sublayer.extent())

        self.import_data_dlg.progressBar.hide()

        self.make_statistic(
            cur_feat_count_bf=cur_feature_count,
            imp_feat_count=imp_feature_count,
            imported_feat=imported_feature_count,
            cur_feat_count_af=cur_sublayer.featureCount(),
            null_geometry=null_geometry_feature_count
        )

        self.iface.messageBar().pushMessage(
            self.config.config_reader["user_messages"]["successful_import_message"],
            level=qgis.core.Qgis.MessageLevel.Success,
            duration=5
        )

    def import_data_run(self):
        self.import_data_dlg.progressBar.hide()
        self.import_data_dlg.activateWindow()

        if not validate_db_and_project_path(
            qgis_project=self.qgis_project,
            dialog=self.import_data_dlg,
            db_combobox=self.import_data_dlg.ImportFileDBcomboBox,
            iface=self.iface
        ):
            return

        self.ui_worker.write_data_in_forestry_object_id_cb()
        self.import_data_dlg.ImportFileDBcomboBox.currentIndexChanged.connect(
            self.ui_worker.write_data_in_forestry_object_id_cb
        )
        self.import_data_dlg.tableWidget.itemDoubleClicked.connect(
            self.ui_worker.write_data_in_table
        )
        self.import_data_dlg.ImportFileDatasourceButton.clicked.connect(
            self.ui_worker.import_data_filemanager_handler
        )
        self.import_data_dlg.ImportFileLayerscomboBox.currentIndexChanged.connect(
            self.ui_worker.check_crs_for_cur_imp_sub_layer
        )
        self.import_data_dlg.ImportFileButton.clicked.connect(
            self.importing_data
        )
        self.import_data_dlg.ImportFileCanceleButton.clicked.connect(
            self.import_data_dlg.close
        )
        self.import_data_dlg.exec()
