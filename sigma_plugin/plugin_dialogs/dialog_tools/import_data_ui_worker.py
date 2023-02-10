from typing import Optional
from pathlib import Path

from qgis.PyQt import QtWidgets, QtCore, QtGui
from qgis.PyQt.Qt import Qt

import qgis.core


from ...help_tools.config_reader import ConfigWorker


def _get_current_import_sub_layer(
        import_sub_layers: list[str],
        import_layer_filepath: str,
        sublayer_name: str,
        sublayer_type: str
) -> qgis.core.QgsVectorLayer:
    if len(import_sub_layers) == 1:
        current_layer_uri: str = (
            f"{import_layer_filepath}|"
            f"layername={sublayer_name}|"
            f"geometrytype={sublayer_type}|"
            f"uniqueGeometryType=yes"
        )
    else:
        current_layer_uri: str = (
            f"{import_layer_filepath}|"
            f"layername={sublayer_name}|"
            f"geometrytype={sublayer_type}"
        )
    return qgis.core.QgsVectorLayer(
                current_layer_uri, sublayer_name, "ogr"
            )


class ImportDataTableDelegator(QtWidgets.QStyledItemDelegate):
    """Class for QTableWidget delegate of import dialog."""

    def __init__(
            self,
            import_data_dialog: QtWidgets.QDialog,
            import_sub_layers: dict[str, qgis.core.QgsVectorLayer]
    ) -> None:

        super().__init__(parent=None)
        self.import_data_dialog: QtWidgets.QDialog = import_data_dialog
        self.table_widget: QtWidgets.QTableWidget = import_data_dialog.tableWidget
        self.import_sub_layers: dict[str, qgis.core.QgsVectorLayer] = import_sub_layers

    def _get_combobox_data(self) -> list:
        sublayer_columns = []
        if self.import_sub_layers:
            import_sublayer = self.import_sub_layers[
                self.import_data_dialog.ImportFileLayerscomboBox.currentText()
            ]
            sublayer_columns.extend(
                [col.name for col in import_sublayer.attributeTableConfig().columns()]
            )
            sublayer_columns.insert(0, "")
            return sublayer_columns
        return sublayer_columns

    def createEditor(
            self, parent: QtWidgets.QWidget,
            option: QtWidgets.QStyleOptionViewItem,
            index: QtCore.QModelIndex
    ) -> QtWidgets.QWidget:
        editor = None

        if index.column() == 1:
            editor = QtWidgets.QComboBox(parent)

        if index.column() == 2:
            editor = QtWidgets.QLineEdit(parent)
            validator: QtGui.QIntValidator = QtGui.QIntValidator()
            # validator.setLocale(QtCore.QLocale("en_US"))
            editor.setValidator(validator)

        return editor

    def setEditorData(
            self,
            editor: QtWidgets.QWidget,
            index: QtCore.QModelIndex,
            autocomplete_value: int = None
    ) -> None:

        value = index.model().data(index, Qt.DisplayRole)
        combobox_data: list = self._get_combobox_data()

        if isinstance(editor, QtWidgets.QComboBox):
            editor.addItems(combobox_data)
            editor.setCurrentText(value)
            if autocomplete_value:
                editor.setCurrentIndex(autocomplete_value)

        else:
            editor.setText(value)

    def setModelData(
            self,
            editor: QtWidgets.QWidget,
            model: QtCore.QAbstractItemModel,
            index: QtCore.QModelIndex
    ) -> None:

        if isinstance(editor, QtWidgets.QComboBox):
            value = editor.currentText()
        else:
            value = editor.text()

        model.setData(index, value, Qt.DisplayRole)

    def updateEditorGeometry(
            self,
            editor: QtWidgets.QWidget,
            option: QtWidgets.QStyleOptionViewItem,
            index: QtCore.QModelIndex
    ) -> None:

        editor.setGeometry(option.rect)

    def clear_table_widget_data(self) -> None:
        for row in range(self.table_widget.rowCount()):
            for column in range(self.table_widget.columnCount())[1:]:
                table_item = self.table_widget.item(row, column)
                table_item.setText("")

    def autocomplete_table_data(self, ac_config: dict) -> None:
        self.clear_table_widget_data()
        combobox_data: list = self._get_combobox_data()

        for row in range(1, self.table_widget.rowCount() + 1):
            column_alias = ac_config.get(str(row), "")
            for alias in column_alias:
                if alias and alias.lower() in {
                    col_name.lower() for col_name in combobox_data
                }:
                    value_index_cb = [
                        col_name.lower() for col_name in combobox_data
                    ].index(alias.lower())

                    index = self.table_widget.indexFromItem(self.table_widget.item(row - 1, 1))
                    option = self.table_widget.viewOptions()
                    widget = self.createEditor(
                        parent=self.table_widget,
                        option=option,
                        index=index
                    )
                    self.setEditorData(
                        editor=widget,
                        index=index,
                        autocomplete_value=value_index_cb
                    )
                    self.setModelData(editor=widget, model=self.table_widget.model(), index=index)
                    self.updateEditorGeometry(editor=widget, option=option, index=index)


class ImportDataUiWorker:
    """Ui worker for Import Data module."""

    def __init__(
            self,
            import_data_dialog: QtWidgets.QDialog,
            qgis_interface: qgis.gui.QgisInterface,
            config: ConfigWorker,
    ) -> None:
        self.import_sub_layers: dict[str, qgis.core.QgsVectorLayer] = {}
        self.import_data_dialog: QtWidgets.QDialog = import_data_dialog
        self.import_data_delegator: ImportDataTableDelegator = ImportDataTableDelegator(
            import_data_dialog=self.import_data_dialog,
            import_sub_layers=self.import_sub_layers
        )
        self.iface: qgis.gui.QgisInterface = qgis_interface
        self.config: ConfigWorker = config
        self.forestry_object_id_data: dict[str, str] = {}
        self.autocomplete_table_data = True

    def _get_import_layer_filepath(self) -> str:
        filemanager_layer_filepath: str = QtWidgets.QFileDialog().getOpenFileName(
            directory=self.config.config_reader["default_file_dlg_dir_path"]
        )[0]

        if filemanager_layer_filepath:
            self.config.config_writer(
                change_field="default_file_dlg_dir_path",
                new_value=Path(filemanager_layer_filepath).parent
            )
        self.import_data_dialog.ImportFileDatasource.clear()
        self.import_data_dialog.ImportFileDatasource.setText(filemanager_layer_filepath)

        return filemanager_layer_filepath

    def _get_import_sub_layers(
            self,
            import_layer: qgis.core.QgsVectorLayer,
            import_layer_filepath: str
    ) -> list[list]:
        import_layer_dp: qgis.core.QgsDataProvider = import_layer.dataProvider()
        import_sub_layers: list[str] = import_layer_dp.subLayers()
        sublayer_sep: str = import_layer_dp.sublayerSeparator()

        sub_layers_data_for_cb: list[list] = []

        for sublayer in import_sub_layers:
            sl_name: str = sublayer.split(sublayer_sep)[1]
            sl_type: str = sublayer.split(sublayer_sep)[3]
            geom_count: str = sublayer.split(sublayer_sep)[2]

            current_sublayer: qgis.core.QgsVectorLayer = _get_current_import_sub_layer(
                import_sub_layers=import_sub_layers,
                import_layer_filepath=import_layer_filepath,
                sublayer_name=sl_name,
                sublayer_type=sl_type
            )
            cb_sublayer_name: str = f"{sl_name} {sl_type} {geom_count}"
            sub_layers_data_for_cb.append(
                [
                    qgis.core.QgsIconUtils().iconForLayer(current_sublayer),
                    cb_sublayer_name
                ]
            )
            self.import_sub_layers.update({cb_sublayer_name: current_sublayer})
        return sub_layers_data_for_cb

    def import_data_filemanager_handler(self) -> None:
        self.autocomplete_table_data = True

        import_layer_filepath: str = self._get_import_layer_filepath()
        import_layer_name: str = import_layer_filepath.split("/")[-1]
        import_layer: qgis.core.QgsVectorLayer = qgis.core.QgsVectorLayer(
            import_layer_filepath, import_layer_name, "ogr"
        )

        if not import_layer.isValid():
            self.import_data_delegator.clear_table_widget_data()
            self.import_data_dialog.ImportFileLayerscomboBox.clear()
            self.import_data_dialog.crsSelector.setCrs(
                qgis.core.QgsCoordinateReferenceSystem("invalid")
            )
            return

        sub_layers_data_for_cb = self._get_import_sub_layers(
            import_layer=import_layer,
            import_layer_filepath=import_layer_filepath
        )
        self.import_data_dialog.ImportFileLayerscomboBox.clear()

        for sub_l_data in sub_layers_data_for_cb:
            self.import_data_dialog.ImportFileLayerscomboBox.addItem(*sub_l_data)

    def write_data_in_forestry_object_id_cb(self) -> None:
        self.import_data_dialog.ImportFileForestObjIdcomboBox.clear()

        current_db_source = self.import_data_dialog.ImportFileDBcomboBox.currentText()
        layer = qgis.core.QgsVectorLayer(
            f"{current_db_source}|layername=data_objects", "data_objects_layer", "ogr"
        )
        data_for_obj_id_cb = []
        for feat in layer.getFeatures():
            try:
                self.forestry_object_id_data[feat.attribute("title")] = feat.attribute("id")
                data_for_obj_id_cb.append(feat.attribute("title"))
            except KeyError:
                try:
                    self.forestry_object_id_data[feat.attribute("name")] = feat.attribute("id")
                    data_for_obj_id_cb.append(feat.attribute("name"))
                except KeyError:
                    self.iface.messageBar().pushMessage(
                        "В базе отсутствуют объекты лесоустройства.",
                        level=qgis.core.Qgis.MessageLevel.Critical,
                        duration=5
                    )
                    return
        data_for_obj_id_cb.insert(0, "")
        self.import_data_dialog.ImportFileForestObjIdcomboBox.addItems(data_for_obj_id_cb)

    def write_data_in_table(self) -> None:
        table_widget: QtWidgets.QTableWidget = self.import_data_dialog.tableWidget
        table_widget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        if not self.import_data_dialog.ImportFileDatasource.text():
            self.iface.messageBar().pushMessage(
                self.config.config_reader["user_messages"]["warning_message_3"],
                level=qgis.core.Qgis.MessageLevel.Warning,
                duration=3
            )
            table_widget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            return

        if self.autocomplete_table_data:
            self.import_data_delegator.autocomplete_table_data(
                ac_config=self.config.config_reader["autocomplete"]
            )
            self.autocomplete_table_data = False
        table_widget.setItemDelegate(self.import_data_delegator)

    def check_crs_for_cur_imp_sub_layer(self) -> None:
        cur_imp_sublayer_name = self.import_data_dialog.ImportFileLayerscomboBox.currentText()
        if cur_imp_sublayer_name == "":
            return

        self.autocomplete_table_data = True
        self.write_data_in_table()

        cur_imp_sublayer = self.import_sub_layers[cur_imp_sublayer_name]
        cur_imp_sublayer_crs = cur_imp_sublayer.crs()

        if cur_imp_sublayer_crs.isValid():
            self.import_data_dialog.crsSelector.setCrs(crs=cur_imp_sublayer_crs)
            self.iface.messageBar().pushMessage(
                self.config.config_reader["user_messages"]["warning_message_2"],
                level=qgis.core.Qgis.MessageLevel.Success,
                duration=3
            )
            return
        self.iface.messageBar().pushMessage(
            self.config.config_reader["user_messages"]["warning_message_1"],
            level=qgis.core.Qgis.MessageLevel.Warning,
            duration=3
        )

    @staticmethod
    def _get_table_item_value(
            column: int, item_obj: QtWidgets.QTableWidgetItem
    ) -> [float, int]:
        item_value: str = item_obj.text()

        if not item_value:
            if column == 1:
                return ""
            else:
                return "0"
        if column in (1, 2) and item_value:
            return item_value

    def get_table_widget_values(self) -> dict:
        table_widget: QtWidgets.QTableWidget = self.import_data_dialog.tableWidget
        table_rows: dict = {
            1: [
                self.forestry_object_id_data[
                    self.import_data_dialog.ImportFileForestObjIdcomboBox.currentText()
                ],
                "0"
            ]
        }
        for row in range(table_widget.rowCount()):
            table_rows.setdefault(row + 2, [])
            for column in range(1, table_widget.columnCount()):
                item_obj: QtWidgets.QTableWidgetItem = table_widget.item(row, column)
                table_rows[row + 2].append(
                    self._get_table_item_value(column=column, item_obj=item_obj)
                )
        return table_rows
