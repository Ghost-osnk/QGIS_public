"""Docstring"""

from typing import List, Dict
from itertools import chain
# import sys

import qgis.core as qgs_core

# sys.path.append("/home/c1/dc/qgis/tasks/task_2/git/result")
# from help_tools.config_reader import ConfigWorker
# from help_tools.help_func import TopologyFeatureData
# from dr_abstract_check import DRAbstractCheck

from ....help_tools.config_reader import ConfigWorker
from ....help_tools.help_func import TopologyFeatureData


class DRDoubledAttributesCheck:
    """Docstring"""

    def __init__(self, config: ConfigWorker, layers: List[qgs_core.QgsVectorLayer]) -> None:

        self.config = config
        self.layers = layers
        self.result_error_list = []

    def check_doubled_attributes(self) -> List[TopologyFeatureData]:
        """Docstring"""

        features_by_layers = []

        for layer in self.layers:
            features = self._get_features(layer=layer)
            self._get_errors_by_layer_features(features=features)
            features_by_layers.append(features)

        self._get_errors_by_intersection_layers(features=features_by_layers)

        return self.result_error_list

    def _get_errors_by_layer_features(
            self,
            features: Dict[tuple, List[TopologyFeatureData]]
    ) -> None:

        doubled_features = list(chain(*(d_feat for d_feat in features.values() if len(d_feat) > 1)))

        for feature in doubled_features:
            self.result_error_list.append(feature)

    def _get_errors_by_intersection_layers(
            self,
            features: List[Dict[tuple, List[TopologyFeatureData]]]
    ) -> None:

        if len(features) > 2:
            pass
        else:

            doubled_features = [
                [features[0][attr], features[1][attr]] for attr in
                set(features[0].keys()).intersection(set(features[1].keys()))
            ]

            for feature in doubled_features:
                self.result_error_list.append(self._merge_data_field(list(chain(*feature))))

    @staticmethod
    def _merge_data_field(data: List[TopologyFeatureData]) -> TopologyFeatureData:

        return TopologyFeatureData(
            layer_name=", ".join({f_data.layer_name for f_data in data}),
            feature_id=", ".join([f_data.feature_id for f_data in data]),
            error_type=", ".join({f_data.error_type for f_data in data}),
            feature_object=[f_data.feature_object for f_data in data]
        )

    def _get_features(
            self,
            layer: qgs_core.QgsVectorLayer
    ) -> Dict[tuple, List[TopologyFeatureData]]:

        features = {}
        current_layer_name = layer.name()

        for feature in layer.getFeatures():
            feature_attributes = tuple(
                feature.attributes()[attr_ind]
                if feature.attributes()[attr_ind] != qgs_core.NULL
                else 0
                for attr_ind in (
                    feature.fieldNameIndex(
                        feat_name
                    ) for feat_name in self.config.config_reader["attributes"]
                )
            )
            feature_obj_dt = TopologyFeatureData(
                layer_name=current_layer_name,
                feature_id=str(feature.id()),
                error_type="Одинаковые адресные атрибуты",
                feature_object=feature
            )
            features.setdefault(feature_attributes, []).append(feature_obj_dt)

        return features
