"""
dr_duplicate_geometry_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm for finding duplicate geometries.
"""

from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes

from ....help_tools.help_func import TopologyFeatureData
from .dr_abstract_check import DRAbstractCheck


class DRDuplicateGeometry(DRAbstractCheck):
    """A class that contains an algorithm for finding duplicate geometries."""

    def run_check(self, layer_name: str, features: List[QgsFeature],
                  feature_ids: List[int], feature_geoms: List[QgsGeometry],
                  optional_param: Any = None, ) -> List[TopologyFeatureData]:
        """Public function from which the execution of the class functionality begins."""

        return super().run_check(layer_name=layer_name, features=features, feature_ids=feature_ids,
                                 feature_geoms=feature_geoms)

    def _run_check(self, layer_name: str, features: List[QgsFeature],
                   feature_ids: List[int], feature_geoms: List[QgsGeometry],
                   optional_param: Any = None, ) -> List[TopologyFeatureData]:

        error_list = []
        feature_ids_copy = feature_ids.copy()
        feature_geoms_copy = feature_geoms.copy()
        error_index = 0

        for index, geom in enumerate(feature_geoms):
            if geom.isEmpty():
                continue
            feat_id = feature_ids[index]

            for index_2, geom_copy in enumerate(feature_geoms_copy):
                if geom_copy.isEmpty():
                    continue
                feat_id_copy = feature_ids_copy[index_2]

                if feat_id != feat_id_copy:
                    if geom.equals(geom_copy):
                        cur_error = TopologyFeatureData(
                            layer_name=layer_name,
                            feature_id=str(feat_id),
                            error_type="Дублирование геометрии",
                            feature_object=features[index],
                            error_coordinate=QgsGeometry().fromPointXY(geom.centroid().asPoint()),
                            meaning=f"{layer_name}:{feat_id_copy}"
                        )
                        setattr(cur_error, "d_id", str(feat_id_copy))
                        setattr(cur_error, "index", error_index)
                        error_index += 1
                        error_list.append(cur_error)

            del feature_ids_copy[0]
            del feature_geoms_copy[0]

        return error_list

    def _post_processing_error(
            self,
            error_list: Union[List[Dict[str, Any]], List[TopologyFeatureData]],
    ) -> List[TopologyFeatureData]:

        result_list = []
        indices_list = []
        used_indeces = []

        for index1, error1 in enumerate(error_list):
            indices_list = []
            feature1 = error1.feature_object
            coordinates1 = error1.error_coordinate

            indices_list.append(error1.feature_id)
            indices_list.append(error1.d_id)

            if not error1.index in used_indeces:
                used_indeces.append(error1.index)
            else:
                continue

            for index2, error2 in enumerate(error_list):
                if index1 != index2:
                    feature2 = error2.feature_object
                    coordinates2 = error2.error_coordinate

                    if feature1.geometry().equals(feature2.geometry()) \
                            and coordinates1.equals(coordinates2):

                        if not error2.index in used_indeces:
                            used_indeces.append(error2.index)
                        else:
                            continue

                        indices_list.append(error2.feature_id)
                        indices_list.append(error2.d_id)

            indices_list = list(set(indices_list))
            if error1.feature_id in indices_list:
                del indices_list[indices_list.index(error1.feature_id)]
            meaning = f'{error1.layer_name}:'

            for element in indices_list:
                meaning = meaning + f"{element},"
            meaning = meaning[:-1]
            if len(indices_list) > 1:
                meaning = meaning + f" Количество дубликатов: {len(indices_list)}"
            error1.meaning = meaning
            result_list.append(error1)

        return super()._post_processing_error(error_list=result_list, )

    def _compatible_geometry_types(self) -> List[int]:

        return [
            QgsWkbTypes.LineString,
            QgsWkbTypes.MultiLineString,
            QgsWkbTypes.Polygon,
            QgsWkbTypes.MultiPolygon,
            QgsWkbTypes.Point,
            QgsWkbTypes.MultiPoint,
        ]
