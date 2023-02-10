import os
from pathlib import Path
from typing import Dict

import qgis.core as qgs_core
import qgis.gui as qgs_gui

from ..plugin_dialogs.dynamic_style_changer_dialog import DynamicStyleChangerDialog
from ..help_tools.help_func import validate_db_and_project_path
from ..help_tools.config_reader import ConfigWorker


class DynamicStyleChangerTool:
    def __init__(self, iface: qgs_gui.QgisInterface, parent_window):
        self.iface = iface
        self.qgis_project = qgs_core.QgsProject().instance()
        self.layer_tree = self.qgis_project.layerTreeRoot()
        self.layers = {layer.name(): layer for layer in self.qgis_project.mapLayers().values()}
        self.rg = self.iface.layerTreeCanvasBridge().rootGroup()
        self.dynamic_style_changer_dlg = DynamicStyleChangerDialog(parent=parent_window)
        self.qml_files_path = Path(__file__).parents[1].joinpath("configs/style_files/qml_files/")
        self.config = ConfigWorker(header='styles').styles_config_reader

    def close_window(self) -> None:
        self.dynamic_style_changer_dlg.close()

    def generate_styles_list(self) -> None:
        for style in self.config:
            self.dynamic_style_changer_dlg.comboBox_2.addItem(style['title'])

    def get_styles_from_config(self, style_name) -> Dict:
        styles = {}
        for style in self.config:
            if style['title'] == style_name:
                for layer in style['layers']:
                    styles[style_name] = layer

        return styles

    def uncheck_not_styled_layers(self, layers_for_styling) -> None:
        for layer in self.layers.values():
            if layer.name() not in layers_for_styling:
                self.layer_tree.findLayer(layer.id()).setItemVisibilityChecked(False)

    def apply_styles(self) -> None:
        style_name = self.dynamic_style_changer_dlg.comboBox_2.currentText()
        styles = self.get_styles_from_config(style_name=style_name)
        layers_for_styling = [layer for layer in styles[style_name].keys()]

        for index, (layer_name, layer_properties) in enumerate(styles[style_name].items()):
            if layer_name in self.layers:
                if layer_properties['file'] in os.listdir(self.qml_files_path):

                    if index == 0:
                        self.uncheck_not_styled_layers(layers_for_styling)

                    self.layers[layer_name].loadNamedStyle(str(self.qml_files_path.joinpath(layer_properties['file'])))
                    self.layers[layer_name].triggerRepaint()

                    layer_in_tree = self.layer_tree.findLayer(self.layers[layer_name].id())
                    clone = layer_in_tree.clone()
                    parent = layer_in_tree.parent()
                    parent.insertChildNode(int(layer_properties['z-index']), clone)
                    parent.removeChildNode(layer_in_tree)

                    self.layer_tree.findLayer(self.layers[layer_name].id()).setItemVisibilityChecked(True)

                else:
                    error_message = 'Qml-файла стилей с названием ' + layer_properties['file'] + ' нет в директории.'
                    self.iface.messageBar().pushMessage(error_message, level=qgs_core.Qgis.Critical, duration=5)

            else:
                error_message = 'Слоя с названием ' + layer_name + ' нет в проекте.'
                self.iface.messageBar().pushMessage(error_message, level=qgs_core.Qgis.Critical, duration=5)

    def dynamic_style_changer_run(self) -> None:
        if not validate_db_and_project_path(
            qgis_project=self.qgis_project,
            dialog=self.dynamic_style_changer_dlg,
            iface=self.iface
        ):
            return

        self.dynamic_style_changer_dlg.activateWindow()

        self.generate_styles_list()
        self.dynamic_style_changer_dlg.pushButton.clicked.connect(self.close_window)
        self.dynamic_style_changer_dlg.pushButton_3.clicked.connect(self.apply_styles)

        self.dynamic_style_changer_dlg.exec()
