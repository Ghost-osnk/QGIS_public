"""
dr_inside_object_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm for finding object with count on vertices less than 3.
"""

from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsWkbTypes

from ....help_tools.help_func import TopologyFeatureData
from .dr_abstract_check import DRAbstractCheck


class DRMissingVertex(DRAbstractCheck):
    """A class that contains an algorithm for finding object with count on vertices less than 3."""

    def run_check(self, layer_name: str, features: List[QgsFeature],
                  feature_ids: List[int], feature_geoms: List[QgsGeometry],
                  optional_param: Any = None, ) -> List[TopologyFeatureData]:
        """Public function from which the execution of the class functionality begins."""

        return super().run_check(layer_name=layer_name, features=features,
                                 feature_ids=feature_ids, feature_geoms=feature_geoms)

    def _run_check(self, layer_name: str, features: List[QgsFeature],
                   feature_ids: List[int], feature_geoms: List[QgsGeometry],
                   optional_param: Any = None, ) -> List[TopologyFeatureData]:

        error_list = []

        for index, geom in enumerate(feature_geoms):
            if geom.isEmpty():
                continue

            if geom.constGet().vertexCount() < 4:
                cur_error = TopologyFeatureData(
                    layer_name=layer_name,
                    feature_id=str(feature_ids[index]),
                    error_type="Полигон числом вершин менее трёх",
                    feature_object=features[index],
                    error_coordinate=QgsGeometry.fromPointXY(QgsPointXY(0.0000000, 0.00000000)),
                )
                error_list.append(cur_error)
        return error_list

    def _post_processing_error(self, error_list: Union[List[Dict[str, Any]],
    List[TopologyFeatureData]]) -> List[TopologyFeatureData]:

        return super()._post_processing_error(error_list=error_list)

    def _compatible_geometry_types(self) -> List[int]:

        return [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon, ]
