"""
dr_intersection_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm for finding intersecting polygons.
"""

from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes

from .dr_abstract_check import DRAbstractCheck
from ....help_tools.help_func import TopologyFeatureData


class DROverlapPolygon(DRAbstractCheck):
    """A class that contains an algorithm for finding intersecting polygons."""

    def run_check(self, layer_name: str, features: List[QgsFeature],
                  feature_ids: List[int], feature_geoms: List[QgsGeometry],
                  optional_param: Any = None, ) -> List[TopologyFeatureData]:
        """Public function from which the execution of the class functionality begins."""

        return super().run_check(
            layer_name=layer_name,
            features=features,
            feature_ids=feature_ids,
            feature_geoms=feature_geoms,
            optional_param=optional_param,
        )

    def _run_check(self, layer_name: str, features: List[QgsFeature],
                   feature_ids: List[int], feature_geoms: List[QgsGeometry],
                   optional_param: Any = None, ) -> List[TopologyFeatureData]:

        error_list = []
        feature_ids_copy = feature_ids.copy()
        feature_geoms_copy = feature_geoms.copy()
        threshold = optional_param

        for index1, geom in enumerate(feature_geoms):
            feat_id = feature_ids[index1]

            for index2, geom_copy in enumerate(feature_geoms_copy):
                feat_id_copy = feature_ids_copy[index2]

                if feat_id != feat_id_copy:

                    intersection_result = geom.intersection(geom_copy)
                    if intersection_result:
                        if intersection_result.type() > 1:
                            if not geom.equals(geom_copy):
                                if not geom.within(geom_copy):
                                    if not geom_copy.within(geom):
                                        polygons = []
                                        if intersection_result.isMultipart():
                                            polygons = intersection_result.asGeometryCollection()
                                        else:
                                            polygons.append(intersection_result)
                                        for polygon in polygons:
                                            if polygon.type() > 1:
                                                area = polygon.area()
                                                if not threshold:
                                                    threshold = 0.0001
                                                if area > 0.0001 and area > threshold:
                                                    cur_error = TopologyFeatureData(
                                                        layer_name=layer_name,
                                                        feature_id=str(feat_id),
                                                        feature_object=features[index1],
                                                        error_type="Перекрытия",
                                                        error_coordinate=QgsGeometry().fromPointXY(
                                                            polygon.centroid().asPoint()),
                                                        meaning=f"{layer_name}:{feat_id_copy}",
                                                    )

                                                    error_list.append(cur_error)

            del feature_geoms_copy[0]
            del feature_ids_copy[0]

        return error_list

    def _post_processing_error(self, error_list: Union[List[Dict[str, Any]],
    List[TopologyFeatureData]]) -> TopologyFeatureData:

        return super()._post_processing_error(error_list=error_list)

    def _compatible_geometry_types(self) -> List[int]:
        return [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]
