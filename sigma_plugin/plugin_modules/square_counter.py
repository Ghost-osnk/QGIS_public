from decimal import Decimal, InvalidOperation
from typing import Dict, Union

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt import QtWidgets
import qgis.core as qgs_core
import qgis.gui as qgs_gui

from ..plugin_dialogs.square_counter_dialog import SquareCounterDialog
from ..help_tools.config_reader import ConfigWorker
from ..help_tools.help_func import validate_db_and_project_path


class SquareCounterTool:
    def __init__(self, iface: qgs_gui.QgisInterface, parent_window):

        self.iface = iface
        self.qgis_project = qgs_core.QgsProject().instance()
        self.project_source = ()
        self.square_counter_dlg = SquareCounterDialog(parent=parent_window)
        self.config = ConfigWorker(header="square_counter_config")

    def _create_area_columns_in_tables(self):

        project_source = self.square_counter_dlg.SquareCounterDBcomboBox.currentText()
        table_names = tuple(
            [
                self.config.get_config_file["plugin_configs"]["layers"]["2"],
                self.config.get_config_file["plugin_configs"]["layers"]["3"]
            ]
        )
        columns = self.config.config_reader["square_fields"]

        for table_name in table_names:
            table = qgs_core.QgsVectorLayer(
                f"{project_source}|{table_name}",
                table_name.split("=")[1],
                "ogr",
            )
            table.startEditing()
            for col in columns:
                if table.fields().indexFromName(col) == -1:
                    table.addAttribute(qgs_core.QgsField(col, QVariant.Double))

            table.commitChanges(stopEditing=False)
        self.qgis_project.instance().reloadAllLayers()

    def count_quarters_polygon_area(self) -> Union[dict, None]:

        project_source = self.square_counter_dlg.SquareCounterDBcomboBox.currentText()
        layer_name = self.config.get_config_file["plugin_configs"]["layers"]["3"]
        current_layer = qgs_core.QgsVectorLayer(
            f"{project_source}|{layer_name}",
            layer_name.split("=")[1],
            "ogr",
        )
        round_num_for_quart = self.square_counter_dlg.SquareCounterQuarterscomboBox.currentText()
        project_area = self.square_counter_dlg.SquareCounterGeneralLineEdit.text()

        config_square_fields = self.config.config_reader["square_fields"]
        fields_for_change = list(
            current_layer.fields().names().index(field) for field in config_square_fields
        )
        config_fields_id = self.config.config_reader["square_fields_for_id"]

        area_calc = qgs_core.QgsDistanceArea()
        area_calc.setSourceCrs(
            crs=self.qgis_project.crs(), context=self.qgis_project.transformContext()
        )
        real_area_for_quart_features = {}

        self.square_counter_dlg.progressBar.setMinimum(0)
        self.square_counter_dlg.progressBar.setMaximum(current_layer.featureCount())
        self.square_counter_dlg.progressBar.show()

        for num, feature in enumerate(current_layer.getFeatures()):

            feature_attr = tuple(
                feature.attributes()[attr_ind]
                if feature.attributes()[attr_ind] != qgs_core.NULL
                else 0
                for attr_ind in (
                    feature.fieldNameIndex(feat_name) for feat_name in config_fields_id
                )
            )
            feature_geometry = feature.geometry()
            if not feature_geometry.isEmpty():

                real_quarter_area = area_calc.measureArea(feature_geometry)
                convert_real_quarter_area = area_calc.convertAreaMeasurement(
                    real_quarter_area, qgs_core.QgsUnitTypes.AreaHectares
                )

                real_area_for_quart_features.setdefault(feature_attr, {}).update(
                    {
                        "feature_id": feature.id(),
                        "real": convert_real_quarter_area,
                        "round": Decimal(
                            convert_real_quarter_area
                        ).quantize(Decimal(round_num_for_quart)),
                        "delta": 0
                    }
                )
                self.square_counter_dlg.progressBar.setValue(num + 1)

        quart_area_sum = sum(v["round"] for v in real_area_for_quart_features.values())

        if project_area:
            try:
                project_area = Decimal(project_area)
            except InvalidOperation:
                user_message = self.config.config_reader["user_messages"]["project_square_mistake"]
                self.iface.messageBar().pushMessage(
                    user_message, level=qgs_core.Qgis.MessageLevel.Critical, duration=7
                )
                return None

            if project_area != quart_area_sum:

                copy_area_quart_features = real_area_for_quart_features.copy()
                difference_for_adding = project_area - quart_area_sum

                for feature_data in copy_area_quart_features.values():

                    feature_percent = Decimal((feature_data["round"] * 100) / quart_area_sum)
                    difference = Decimal((feature_percent * difference_for_adding) / 100)

                    feature_data["round"] += difference.quantize(Decimal(round_num_for_quart))
                    feature_data["delta"] = abs(
                        Decimal(feature_data["real"]) - feature_data["round"]
                    )

                sorted_delta_quarter = {
                    k: copy_area_quart_features[k]
                    for k in sorted(
                        copy_area_quart_features,
                        key=lambda x: copy_area_quart_features[x]["delta"],
                        reverse=True
                    )
                }
                rounded_sum = sum(v["round"] for v in copy_area_quart_features.values())
                last_remain = rounded_sum - project_area

                first_quart_key = next(iter(sorted_delta_quarter.keys()))
                sorted_delta_quarter[first_quart_key]["round"] -= last_remain.quantize(
                    Decimal(round_num_for_quart)
                )
                self._save_area_without_changes(
                    current_layer=current_layer,
                    features_area=sorted_delta_quarter.values(),
                    fields_for_change=fields_for_change
                )
                return sorted_delta_quarter
        else:
            self._save_area_without_changes(
                current_layer=current_layer,
                features_area=real_area_for_quart_features.values(),
                fields_for_change=fields_for_change,
            )
            return real_area_for_quart_features

    def count_allotments_polygon_area(self, quarters_data: Union[Dict[tuple, dict], None]):

        if quarters_data is None:
            return None
        project_source = self.square_counter_dlg.SquareCounterDBcomboBox.currentText()
        round_num_for_allot = self.square_counter_dlg.SquareCounterAllotmentscomboBox.currentText()

        layer_name = self.config.get_config_file["plugin_configs"]["layers"]["2"]
        current_layer = qgs_core.QgsVectorLayer(
            f"{project_source}|{layer_name}",
            layer_name.split("=")[1],
            "ogr",
        )
        config_square_fields = self.config.config_reader["square_fields"]
        fields_for_change = list(
            current_layer.fields().names().index(field) for field in config_square_fields
        )
        config_fields_id = self.config.config_reader["square_fields_for_id"]

        area_calc = qgs_core.QgsDistanceArea()
        area_calc.setSourceCrs(
            crs=self.qgis_project.crs(), context=self.qgis_project.transformContext()
        )
        real_area_for_allot_features = {}

        self.square_counter_dlg.progressBar.setMinimum(0)
        self.square_counter_dlg.progressBar.setMaximum(current_layer.featureCount())
        self.square_counter_dlg.progressBar.show()

        for num, feature in enumerate(current_layer.getFeatures()):
            fixed_field_index = int(current_layer.fields().names().index("Фиксированная площадь выдела"))
            area_rounded_index = int(current_layer.fields().names().index("square_rounded"))
            fixed = feature.attributes()[fixed_field_index]

            feature_attr = tuple(
                feature.attributes()[attr_ind]
                if feature.attributes()[attr_ind] != qgs_core.NULL
                else 0
                for attr_ind in (
                    feature.fieldNameIndex(feat_name) for feat_name in config_fields_id
                )
            )
            feature_geometry = feature.geometry()
            if not feature_geometry.isEmpty():

                real_area_for_allot = area_calc.measureArea(feature_geometry)
                convert_real_quarter_area = area_calc.convertAreaMeasurement(
                    real_area_for_allot, qgs_core.QgsUnitTypes.AreaHectares
                )
                real_area_for_allot_features.setdefault(feature_attr, {}).update(
                    {
                        feature.id(): {
                            "feature_id": feature.id(),
                            "real": convert_real_quarter_area,
                            "round": Decimal(
                                convert_real_quarter_area
                            ).quantize(Decimal(round_num_for_allot))
                            if not fixed
                            else Decimal(str(feature.attributes()[area_rounded_index])),
                            "delta": 0,
                            "fixed": fixed
                        }
                    }
                )
                self.square_counter_dlg.progressBar.setValue(num + 1)

        self.square_counter_dlg.progressBar.hide()
        copy_area_allot_features = real_area_for_allot_features.copy()

        for quarter, allotments in copy_area_allot_features.items():

            quarter_area = quarters_data[quarter]["round"]
            allotments_area_sum = sum(allot["round"] for allot in allotments.values())
            difference_for_adding = quarter_area - allotments_area_sum

            for allotment in allotments.values():

                if difference_for_adding == 0:
                    if not allotment["fixed"]:
                        allotment["round"] = allotment["round"].quantize(Decimal(round_num_for_allot))
                else:
                    feature_percent = (allotment["round"] * 100) / allotments_area_sum
                    difference = (feature_percent * difference_for_adding) / 100
                    if not allotment["fixed"]:
                        allotment["round"] += difference.quantize(Decimal(round_num_for_allot))

                allotment["delta"] = abs(Decimal(allotment["real"]) - allotment["round"])

        for quarter, allotments in copy_area_allot_features.items():

            quarter_area = quarters_data[quarter]["round"]
            allotments_area_sum = sum(allot["round"] for allot in allotments.values())
            last_remain = allotments_area_sum - quarter_area

            sorted_delta_allotment = sorted(
                allotments.keys(), key=lambda x: allotments[x]["delta"], reverse=True
            )
            quart_key = next(iter(sorted_delta_allotment))
            if not allotments[quart_key]["fixed"]:
                allotments[quart_key]["round"] -= last_remain.quantize(Decimal(round_num_for_allot))

        write_in_table = {}

        for quart in copy_area_allot_features.values():
            for allot_id, allot_data in quart.items():
                write_in_table[allot_id] = allot_data

        self._save_area_without_changes(
            current_layer=current_layer,
            features_area=write_in_table.values(),
            fields_for_change=fields_for_change,
        )
        return write_in_table

    def _save_area_without_changes(
            self,
            current_layer: qgs_core.QgsVectorLayer,
            features_area,
            fields_for_change: list,
    ):

        current_layer.startEditing()

        for area_data in features_area:
            current_layer.changeAttributeValues(
                fid=area_data["feature_id"],
                newValues={
                    fields_for_change[0]: float(area_data["real"]),
                    fields_for_change[1]: float(area_data["round"]),
                    fields_for_change[2]: float(area_data["delta"]),
                }
            )

        if current_layer.commitChanges(stopEditing=True):
            user_message = self.config.config_reader["user_messages"]["successful_write"]
            self.iface.messageBar().pushMessage(
                user_message, level=qgs_core.Qgis.Success, duration=7
            )
        else:
            user_message = " ".join(current_layer.commitErrors())
            self.iface.messageBar().pushMessage(
                user_message, level=qgs_core.Qgis.Critical, duration=7
            )
            current_layer.rollBack()

    def set_values_in_combobox(self):

        round_values = self.config.config_reader["round_values"]
        for val in round_values:

            self.square_counter_dlg.SquareCounterAllotmentscomboBox.addItem(val)
            self.square_counter_dlg.SquareCounterQuarterscomboBox.addItem(val)

    def setup_backend(self):
        # TODO Обработка ошибки при которой отсутствуют слои
        quarters_data = self.count_quarters_polygon_area()
        allotment_data = self.count_allotments_polygon_area(quarters_data=quarters_data)

        self.remember_settings()
        self.make_statistic(
            quarters_data=quarters_data,
            allotments_data=allotment_data
        )

        self.qgis_project.reloadAllLayers()

    def close_window(self):
        self.square_counter_dlg.close()

    def make_statistic(
            self,
            quarters_data: dict,
            allotments_data: dict,
    ):
        quantize_num = Decimal("0.000001")

        quarters_real = sum(q_real["real"] for q_real in quarters_data.values())
        quarters_round = sum(q_real["round"] for q_real in quarters_data.values())
        quarters_round_value = self.square_counter_dlg.SquareCounterQuarterscomboBox.currentText()
        quarters_different = abs(
            Decimal(quarters_real).quantize(
                quantize_num
            ) - quarters_round.quantize(Decimal(quarters_round_value))
        )

        allotment_real = sum(a_real["real"] for a_real in allotments_data.values())
        allotment_round = sum(a_real["round"] for a_real in allotments_data.values())
        allotment_round_value = self.square_counter_dlg.SquareCounterQuarterscomboBox.currentText()
        allotment_different = abs(
            Decimal(allotment_real).quantize(
                quantize_num
            ) - allotment_round.quantize(Decimal(allotment_round_value))
        )

        self.square_counter_dlg.tabWidget.setCurrentIndex(1)

        template = self.config.config_reader["user_messages"]["result_tab"]
        result = (
            f"{template['quarters_real']} "
            f"{Decimal(quarters_real).quantize(quantize_num)} га.\n"
            f"{template['quarters_round']} "
            f"{quarters_round.quantize(Decimal(quarters_round_value))} га.\n"
            f"{template['quarters_different']} "
            f"{quarters_different} га.\n"
            "\n"
            f"{template['allotment_real']} "
            f"{Decimal(allotment_real).quantize(quantize_num)} га.\n"
            f"{template['allotment_round']} "
            f"{allotment_round.quantize(Decimal(allotment_round_value))} га.\n"
            f"{template['allotment_different']} "
            f"{allotment_different} га.\n"
            "\n"
            f"{template['delimiter'] * 20}\n"
        )
        self.square_counter_dlg.textResult.insertPlainText(result)

    def remember_settings(self, autocomplete=False):

        combobox_objects = [
            *list(x for x in self.square_counter_dlg.groupBox_2.findChildren(QtWidgets.QComboBox)),
            *list(x for x in self.square_counter_dlg.groupBox_3.findChildren(QtWidgets.QLineEdit))
        ]
        combobox_field_name = "remember_settings"

        if autocomplete:
            for cb_name, value in self.config.config_reader[combobox_field_name].items():
                for obj in combobox_objects:
                    if cb_name == obj.objectName():
                        if isinstance(obj, QtWidgets.QComboBox):
                            obj.setCurrentIndex(value)
                        if isinstance(obj, QtWidgets.QLineEdit):
                            obj.setText(value)
        else:
            checkbox_settings = {}
            for obj in combobox_objects:
                if isinstance(obj, QtWidgets.QComboBox):
                    checkbox_settings[obj.objectName()] = obj.currentIndex()
                if isinstance(obj, QtWidgets.QLineEdit):
                    checkbox_settings[obj.objectName()] = obj.text()
            self.config.config_writer(change_field=combobox_field_name, new_value=checkbox_settings)

    def square_counter_run(self):

        if not validate_db_and_project_path(
                qgis_project=self.qgis_project,
                dialog=self.square_counter_dlg,
                db_combobox=self.square_counter_dlg.SquareCounterDBcomboBox,
                iface=self.iface
        ):
            return

        self.square_counter_dlg.progressBar.hide()
        self.square_counter_dlg.activateWindow()

        self.set_values_in_combobox()
        self._create_area_columns_in_tables()
        self.remember_settings(autocomplete=True)

        self.square_counter_dlg.SquareCounterButton.clicked.connect(self.setup_backend)
        self.square_counter_dlg.SquareCounterCanceleButton.clicked.connect(
            self.close_window
        )
        self.square_counter_dlg.exec()
