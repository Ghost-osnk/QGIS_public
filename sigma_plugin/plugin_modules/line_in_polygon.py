import datetime
from operator import itemgetter

from qgis import core, gui
# import qgis.PyQt.QtWidgets as QtWidgets

from ..plugin_dialogs.line_in_polygon_dialog import LineInPolygonDialog
from ..help_tools.config_reader import ConfigWorker
from ..help_tools.help_func import validate_db_and_project_path, get_geometry_layer_from_db
from ..plugin_modules.line_to_polygon_module.dr_line_to_polygon import LineToPolygon
from ..help_tools.help_func import LineToPolygonData


class LineInPolygonTool:
    """Class for make polygons from lines."""

    def __init__(self, iface, parent_window):
        self.iface: gui.QgisInterface = iface
        self.qgis_project: core.QgsProject = core.QgsProject().instance()
        self.line_in_poly_dlg = LineInPolygonDialog(parent=parent_window)
        self.config = ConfigWorker(header="plugin_configs").config_reader
        self.error_feature_list: list[dict] = []
        self.result_lines: list[dict] = []

    def setup_combobox(self):
        possible_nodes_num = tuple(range(1, 8))
        self.line_in_poly_dlg.NodeNumComboBox.addItems(map(str, possible_nodes_num))
        self.line_in_poly_dlg.buffer_size.setText("0")
        self.line_in_poly_dlg.angle_size.setText("0")

    def make_result_statistic(self):
        result: str = (
            f"В таблице {self.error_feature_list[0]['layer_name']} "
            f"некорректные атрибутивные данные у "
            f"{self.error_feature_list[0]['wrong_feature']} объектов.\n"
            f"Id объектов: {self.error_feature_list[0]['features_id']}.\n"
            f"Количество корректных объектов: {self.error_feature_list[0]['corr_features']}.\n"
            f"В таблице {self.error_feature_list[1]['layer_name']} "
            f"найдено совпадений по атрибутивным данным у "
            f"{self.error_feature_list[1]['feature_count']} объектов.\n"
            "_____________________________\n"
            # f"Объекты с буфером: {self.error_feature_list[2]['f_width']}.\n"
            # f"Объекты без буфера: {self.error_feature_list[2]['nf_width']}.\n"
            # f"Id объектов без буфера: {self.error_feature_list[2]['nb_feature_id']}.\n"
        )
        self.line_in_poly_dlg.tabWidget.setCurrentIndex(1)
        self.line_in_poly_dlg.textResult.insertPlainText(result)

    def _get_geo_quarters_polygon(
            self,
            address_attributes: list[str, ...]
    ) -> dict[tuple[int, ...], core.QgsFeature]:
        geo_quarters_polygon_layer: core.QgsVectorLayer = get_geometry_layer_from_db(
            qgis_project=self.qgis_project,
            db_combobox=self.line_in_poly_dlg.LineInPolyDBcomboBox,
            geom_type=3
        )

        address_attributes: list[str, ...] = address_attributes.copy()
        address_attributes.remove("allotment")

        quarters_features: dict[tuple[int, ...], core.QgsFeature] = {}

        for feature in geo_quarters_polygon_layer.getFeatures():
            feature_key: tuple[int, ...] = tuple(feature[f_attr] for f_attr in address_attributes)
            quarters_features[feature_key] = feature

        return quarters_features

    def _make_prepared_data_allotments_features(
            self,
            address_attributes: list[str, ...]
    ) -> None:
        priority_attribute: str = "ground_category_code"
        data_allotment_layer: core.QgsVectorLayer = get_geometry_layer_from_db(
            qgis_project=self.qgis_project,
            db_combobox=self.line_in_poly_dlg.LineInPolyDBcomboBox,
            layer_name="data_allotments"
        )
        data_allotments_errors: dict = {
            "layer_name": data_allotment_layer.name(),
            "feature_count": 0,
            "features_id": []
        }
        data_allotments_features: dict[tuple, core.QgsFeature] = {}

        for feature in data_allotment_layer.getFeatures():
            feature_key: tuple[int, ...] = tuple(feature[f_attr] for f_attr in address_attributes)
            data_allotments_features[feature_key] = feature

        for feature_data in self.result_lines:
            feature_key: tuple[int, ...] = feature_data["address_attributes"]
            if feature_key in data_allotments_features:
                data_allotment_feature: core.QgsFeature = data_allotments_features[feature_key]
                feature_data["d_m13_allotment_id"] = data_allotment_feature.id()
                feature_data["feature_priority"] = data_allotment_feature[priority_attribute]
                data_allotments_errors["feature_count"] += 1

        self.error_feature_list.append(data_allotments_errors)

    def _make_prepared_data_m13_features(self) -> None:
        data_m13_layer: core.QgsVectorLayer = get_geometry_layer_from_db(
            qgis_project=self.qgis_project,
            db_combobox=self.line_in_poly_dlg.LineInPolyDBcomboBox,
            layer_name="data_m13"
        )
        attributes: tuple[str, ...] = ("allotment_id", "width", "ord")
        f_req = core.QgsFeatureRequest().setFilterExpression('"ord"=0')

        data_m13_features: dict[int, int] = {}

        for feature in data_m13_layer.getFeatures(f_req):
            data_m13_features[feature[attributes[0]]] = feature[attributes[1]] // 10

        for feature_data in self.result_lines:
            line_width: int = data_m13_features[feature_data["d_m13_allotment_id"]]
            feature_data["width"] = line_width

    def _make_geo_allotments_lines_features(
            self,
            address_attributes: list[str, ...]
    ) -> core.QgsVectorLayer:
        geo_allotments_line_layer: core.QgsVectorLayer = get_geometry_layer_from_db(
            qgis_project=self.qgis_project,
            db_combobox=self.line_in_poly_dlg.LineInPolyDBcomboBox,
            geom_type=1
        )
        line_feature_error: dict = {
            "layer_name": geo_allotments_line_layer.name(),
            "wrong_feature": 0,
            "features_id": [],
            "corr_features": 0
        }

        for feature in geo_allotments_line_layer.getFeatures():
            line_feature_data: dict = {}
            feature_key: tuple[int, ...] = tuple(feature[f_attr] for f_attr in address_attributes)
            if core.NULL not in feature_key:
                line_feature_data["address_attributes"] = feature_key
                line_feature_data["line_feature"] = feature
                self.result_lines.append(line_feature_data)
            else:
                line_feature_error["features_id"].append(feature.id())
                line_feature_error["wrong_feature"] += 1

        line_feature_error[
            "corr_features"
        ] = geo_allotments_line_layer.featureCount() - line_feature_error["wrong_feature"]
        self.error_feature_list.append(line_feature_error)

        return geo_allotments_line_layer

    def _sort_lines(self) -> list[dict]:
        lines_features: list[dict] = self.result_lines.copy()
        result_list: list[dict] = []

        for feature_data in lines_features:
            if feature_data["feature_priority"] == 2109:
                result_list.append(feature_data)
                lines_features.remove(feature_data)

        for feature_data in lines_features:
            if feature_data["feature_priority"] == 2110:
                result_list.append(feature_data)
                lines_features.remove(feature_data)
        # result_list.extend(list(sorted(lines_features, key=itemgetter("width"), reverse=True)))

        return result_list

    def get_prepared_data(self) -> dict:
        address_attributes: list[str] = self.config["address_attributes"]

        quarters_layer_features = self._get_geo_quarters_polygon(
            address_attributes=address_attributes
        )
        geo_allotments_lines: core.QgsVectorLayer = self._make_geo_allotments_lines_features(
            address_attributes=address_attributes
        )
        self._make_prepared_data_allotments_features(
            address_attributes=address_attributes
        )
        self._make_prepared_data_m13_features()

        for feature_data in self.result_lines:
            quarter_feature_key: tuple[int, ...] = feature_data["address_attributes"][:-1]
            feature_data["quarter_feature"] = quarters_layer_features[quarter_feature_key]

        result_sorted_lines: list[dict] = self._sort_lines()

        result: dict = {
            "crs": geo_allotments_lines.crs(),
            "field_list": geo_allotments_lines.fields().toList(),
            "data_line_to_polygon": LineToPolygonData(
                line_features=[f["line_feature"] for f in result_sorted_lines],
                buffers_size=[f["width"] for f in result_sorted_lines],
                quarters_features=[f["quarter_feature"] for f in result_sorted_lines]
            )
        }
        self.make_result_statistic()

        return result

    def line_to_polygon(self):
        line_worker = LineToPolygon()

        line_data_to_polygon: dict = self.get_prepared_data()
        current_polygon_features = line_worker.line_to_polygon(
            line_data_to_polygon["data_line_to_polygon"]
        )
        new_layer = core.QgsVectorLayer(
            "Polygon?crs=epsg:4326",
            "Buffered_lines",
            "memory"
        )
        if current_polygon_features.polygon_features:
            new_layer.startEditing()
            new_layer.setCrs(line_data_to_polygon["crs"])

            new_layer_dp = new_layer.dataProvider()
            new_layer_dp.addAttributes(line_data_to_polygon["field_list"])

            new_layer_dp.addFeatures(current_polygon_features.polygon_features)
            # new_layer_dp.reloadData()
            new_layer.commitChanges(stopEditing=True)

            self.qgis_project.addMapLayer(new_layer)
            self.qgis_project.reloadAllLayers()

    def line_in_polygon_run(self):
        if not validate_db_and_project_path(
                qgis_project=self.qgis_project,
                dialog=self.line_in_poly_dlg,
                db_combobox=self.line_in_poly_dlg.LineInPolyDBcomboBox,
                iface=self.iface
        ):
            return

        self.line_in_poly_dlg.progressBar.hide()
        self.line_in_poly_dlg.activateWindow()

        self.setup_combobox()
        self.line_in_poly_dlg.LineInPolyCanceleButton.clicked.connect(
            self.line_in_poly_dlg.close
        )
        self.line_in_poly_dlg.LineInPolyButton.clicked.connect(self.line_to_polygon)
        self.line_in_poly_dlg.exec()
