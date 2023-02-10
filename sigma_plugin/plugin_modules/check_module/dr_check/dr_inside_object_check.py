"""
dr_inside_object_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm for finding object inside object.
"""

from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes

from ....help_tools.help_func import TopologyFeatureData
from .dr_abstract_check import DRAbstractCheck


class DRInsideObject(DRAbstractCheck):
    """A class that contains an algorithm for finding object inside object."""

    def run_check(self, layer_name: str, features: List[QgsFeature],
                  feature_ids: List[int], feature_geoms: List[QgsGeometry],
                  optional_param: Any = None, ) -> List[TopologyFeatureData]:
        """Public function from which the execution of the class functionality begins."""

        return super().run_check(layer_name=layer_name, features=features,
                                 feature_ids=feature_ids, feature_geoms=feature_geoms, )

    def _run_check(self, layer_name: str, features: List[QgsFeature],
                   feature_ids: List[int], feature_geoms: List[QgsGeometry],
                   optional_param: Any = None, ) -> List[TopologyFeatureData]:

        error_index = 0
        error_list = []
        feature_ids_copy = feature_ids.copy()
        feature_geoms_copy = feature_geoms.copy()

        for index1, geom in enumerate(feature_geoms):
            feat_id = feature_ids[index1]

            for index2, geom_copy in enumerate(feature_geoms_copy):
                feat_id_copy = feature_ids_copy[index2]

                if feat_id != feat_id_copy:

                    if geom_copy.boundingBoxIntersects(geom.boundingBox()):
                        if not geom.equals(geom_copy):
                            if geom.within(geom_copy):
                                cur_error = TopologyFeatureData(
                                    layer_name=layer_name,
                                    feature_id=str(feat_id),
                                    feature_object=features[index1],
                                    error_type="Находится внутри",
                                    error_coordinate=QgsGeometry().fromPointXY(geom.centroid().asPoint()),
                                    meaning=f"{layer_name}:{feat_id_copy}",
                                )
                                setattr(cur_error, "d_id", str(feat_id_copy))
                                setattr(cur_error, "index", error_index)
                                error_index += 1
                                error_list.append(cur_error)

                            elif geom_copy.within(geom):
                                cur_error = TopologyFeatureData(
                                    layer_name=layer_name,
                                    feature_id=str(feat_id_copy),
                                    feature_object=features[index2],
                                    error_type="Находится внутри",
                                    error_coordinate=QgsGeometry().fromPointXY(geom_copy.centroid().asPoint()),
                                    meaning=f"{layer_name}:{feat_id}",
                                )
                                setattr(cur_error, "d_id", str(feat_id))
                                setattr(cur_error, "index", error_index)
                                error_index += 1
                                error_list.append(cur_error)

        return error_list

    def _post_processing_error(self, error_list: Union[List[Dict[str, Any]],
    List[TopologyFeatureData]]) -> TopologyFeatureData:

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

                    if feature1.geometry().equals(feature2.geometry()) and coordinates1.equals(coordinates2):

                        if not error2.index in used_indeces:
                            used_indeces.append(error2.index)
                        else:
                            continue

                        indices_list.append(error2.feature_id)
                        indices_list.append(error2.d_id)

            # indices_list = list(set(indices_list))
            # feature_id = indices_list[0]
            del indices_list[0]

            result_list.append(error1)

        return super()._post_processing_error(error_list=result_list, )

    def _compatible_geometry_types(self) -> List[int]:

        return [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon, ]
