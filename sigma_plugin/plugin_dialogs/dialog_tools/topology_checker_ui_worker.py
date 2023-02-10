from typing import List

from PyQt5 import QtWidgets, QtCore, QtGui

import qgis.gui as qgs_qui
import qgis.core as qgs_core

from ...plugin_modules.check_module.dr_fixing.dr_error_fixing import DRErrorFixing, DRFixingTypeList

from ...help_tools.help_func import TopologyFeatureData, get_geometry_layer_from_db
from ...help_tools.config_reader import ConfigWorker


class TopologyCheckerUiWorker:
    """Class for QTableWidget interaction of Topology checker dialog."""

    def __init__(
            self,
            table_widget: QtWidgets.QTableWidget,
            errors_list: List[TopologyFeatureData],
            iface: qgs_qui.QgisInterface,
            config: ConfigWorker,
            db_combobox: QtWidgets.QComboBox
    ) -> None:

        self.table_widget = table_widget
        self.qgis_project = qgs_core.QgsProject.instance()
        self.errors_features_list = errors_list
        self.iface = iface
        self.config = config
        self.db_combobox = db_combobox
        self.selected_errors = []
        self.error_fixer = DRErrorFixing()
        # self.menu_action = []

    def _make_action(
            self,
            label_text: str,
            callback_func: object,
            enabled_flag=True
    ) -> QtWidgets.QAction:

        menu_action = QtWidgets.QAction(label_text, self.table_widget)
        menu_action.triggered.connect(callback_func)
        menu_action.setEnabled(enabled_flag)
        # self.menu_action.append(menu_action)

        return menu_action

    def _commit_changes(self, fixed_features: dict):

        for layer_name in fixed_features:
            current_layer = get_geometry_layer_from_db(
                qgis_project=self.qgis_project,
                db_combobox=self.db_combobox,
                layer_name=layer_name
            )
            cur_layer_dp = current_layer.dataProvider()
            current_layer.startEditing()
            cur_layer_dp.deleteFeatures(
                [feat.id() for feat in fixed_features[layer_name]]
            )
            cur_layer_dp.addFeatures(fixed_features[layer_name])
            current_layer.commitChanges(stopEditing=True)

    def _delete_duplicate_nodes(self):

        dup_nodes_errors = [
            error for error in self.selected_errors if error.error_type == "Дублирование вершины"
        ]
        fixed_nodes_errors = self.error_fixer.run_fixing(
            fixing_types=[DRFixingTypeList.delete_nodes],
            fix_error_list=dup_nodes_errors
        )
        to_commit_changes = {}

        for fix_error in fixed_nodes_errors:
            to_commit_changes.setdefault(
                fix_error.layer_name, []
            ).append(fix_error.feature_object)

        self._commit_changes(fixed_features=to_commit_changes)

    # def _delete_duplicate_geometries(self):
    #
    #     dup_geom_errors = (
    #         error for error in self.selected_errors if error.error_type == "Дублирование геометрии"
    #     )
    #     print(dup_geom_errors)

    def _zaglushka(self):
        pass

    def _get_selected_errors(self) -> list:

        selected_table_items = self.table_widget.selectedItems()
        selected_items = {}
        for item in selected_table_items:
            if item.column() in (1, 2):
                selected_items.setdefault(item.row(), []).append(
                    item.data(QtCore.Qt.ItemDataRole.DisplayRole)
                )

        selected_features = [
            error_feature for error_feature in self.errors_features_list
            if [error_feature.feature_id, error_feature.error_type]
            in list(selected_items.values())
        ]

        return selected_features

    def run_table_menu(self, mouse_coord: QtCore.QPoint):

        self.selected_errors = self._get_selected_errors()
        selected_errors_types = set(error.error_type for error in self.selected_errors)

        context_menu = QtWidgets.QMenu(parent=self.table_widget)
        actions = {
            "Дублирование вершины": self._make_action(
                label_text="Удалить дублирующиеся вершины",
                callback_func=self._delete_duplicate_nodes
            ),
            # "Дублирование геометрии": self._make_action(
            #     label_text="Удалить дублирующиеся геометрии",
            #     callback_func=self._delete_duplicate_geometries
            # ),
            "can't_fix": self._make_action(
                label_text="Нет подходящих исправлений",
                callback_func=self._zaglushka,
                enabled_flag=False
            ),
            # "fix_all": self._make_action(
            #     label_text="Исправить все",
            #     callback_func=self._fix_all
            # )
        }

        can_fix_error_types = set(actions.keys())

        if selected_errors_types.issubset(can_fix_error_types):
            for error_type in selected_errors_types:
                context_menu.addAction(actions[error_type])
        else:
            context_menu.addAction(actions["can't_fix"])

        context_menu.exec(self.table_widget.sender().mapToGlobal(mouse_coord))

    def insert_errors_data_in_table(self) -> None:

        field_names = TopologyFeatureData().get_field_names_for_insert

        columns_num = self.table_widget.columnCount()
        rows_num = self.table_widget.rowCount()

        for error in self.errors_features_list:
            error_data = list(str(getattr(error, x)) for x in field_names)
            self.table_widget.insertRow(rows_num)

            for column in range(columns_num):
                item = QtWidgets.QTableWidgetItem()
                item.setText(error_data[column])
                self.table_widget.setItem(rows_num, column, item)

    def make_highlights(self):

        self._remove_highlights()

        error_id = self.table_widget.item(self.table_widget.currentRow(), 1).text()
        error_type = self.table_widget.item(self.table_widget.currentRow(), 2).text()

        for feature_data in self.errors_features_list:
            if feature_data.feature_id == error_id and feature_data.error_type == error_type:
                if isinstance(feature_data.feature_object, list):
                    highlights_list = []
                    hl_bbox = qgs_core.QgsRectangle()
                    for feature in feature_data.feature_object:
                        highlight = self._make_highlight_obj(geometry=feature.geometry())
                        highlights_list.append(highlight)
                        hl_bbox.combineExtentWith(feature.geometry().boundingBox())
                    feature_data.highlight = highlights_list
                    self.iface.mapCanvas().setExtent(hl_bbox)
                    self.iface.mapCanvas().refresh()

                else:
                    if feature_data.error_coordinate:
                        self._make_vertex_marker_obj(feature_data.error_coordinate)

                    feature_data.highlight = self._make_highlight_obj(
                        feature_data.feature_object.geometry()
                    )
                    self.iface.mapCanvas().setExtent(
                        feature_data.feature_object.geometry().boundingBox()
                    )
                    self.iface.mapCanvas().refresh()

    def _make_vertex_marker_obj(self, node_coord: qgs_core.QgsPointXY):

        if isinstance(node_coord, qgs_core.QgsGeometry):
            node_coord = node_coord.asPoint()

        vertex_marker_obj = qgs_qui.QgsVertexMarker(self.iface.mapCanvas())
        vertex_marker_obj.setColor(QtGui.QColor("blue"))
        vertex_marker_obj.setCenter(node_coord)
        vertex_marker_obj.setIconType(qgs_qui.QgsVertexMarker.ICON_CROSS)
        vertex_marker_obj.setIconSize(25)
        vertex_marker_obj.setPenWidth(5)
        vertex_marker_obj.setFillColor(QtGui.QColor("blue"))
        vertex_marker_obj.updateCanvas()

    def _make_highlight_obj(self, geometry: qgs_core.QgsGeometry):

        feature_geometry = geometry
        current_layer = get_geometry_layer_from_db(
            qgis_project=self.qgis_project,
            geom_type=feature_geometry.type(),
            db_combobox=self.db_combobox
        )

        highlight = qgs_qui.QgsHighlight(
            self.iface.mapCanvas(), feature_geometry, current_layer
        )
        color = QtGui.QColor("red")
        highlight.setColor(color)
        color.setAlpha(50)
        highlight.updateCanvas()

        return highlight

    def _remove_highlights(self):

        for error in self.errors_features_list:
            if error.highlight:
                if isinstance(error.highlight, list):
                    for highlight in error.highlight:
                        self.iface.mapCanvas().scene().removeItem(highlight)
                    error.highlight = None
                else:
                    self.iface.mapCanvas().scene().removeItem(error.highlight)
                    error.highlight = None

        for canvas_item in self.iface.mapCanvas().scene().items():
            if isinstance(canvas_item, (qgs_qui.QgsHighlight, qgs_qui.QgsVertexMarker)):
                self.iface.mapCanvas().scene().removeItem(canvas_item)

    def refresh_table_and_errors(self):

        self.table_widget.setRowCount(0)
        self.errors_features_list.clear()
