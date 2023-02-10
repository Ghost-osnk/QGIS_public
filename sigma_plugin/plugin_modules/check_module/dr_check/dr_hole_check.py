"""
dr_hole_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm for finding holes on geometries.
"""

from typing import List, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes

from .dr_abstract_check import DRAbstractCheck
from ....help_tools.help_func import TopologyFeatureData


class DRHoleCheck(DRAbstractCheck):
    """A class that contains an algorithm for finding holes on geometries."""

    def run_check(self, layer_name: str, features: List[QgsFeature],
                  feature_ids: List[int], feature_geoms: List[QgsGeometry],
                  optional_param: Any = None, ) -> List[TopologyFeatureData]:
        """Public function from which the execution of the class functionality begins."""

        return super().run_check(
            layer_name=layer_name,
            features=features,
            feature_ids=feature_ids,
            feature_geoms=feature_geoms,
        )

    def _run_check(self, layer_name: str, features: List[QgsFeature],
                   feature_ids: List[int], feature_geoms: List[QgsGeometry],
                   optional_param: Any = None, ) -> List[TopologyFeatureData]:

        error_list = []

        for index, geom in enumerate(feature_geoms):
            if geom.isEmpty():
                continue

            if len(geom.asMultiPolygon()[0]) != 1:
                for i in range(1, len(geom.asMultiPolygon()[0])):
                    hole = QgsGeometry.fromPolylineXY(geom.asMultiPolygon()[0][i])
                    cur_error = TopologyFeatureData(
                        layer_name=layer_name,
                        feature_id=str(feature_ids[index]),
                        error_type="Полигон с отверстием",
                        feature_object=features[index],
                        error_coordinate=QgsGeometry.fromPointXY(hole.centroid().asPoint()),
                    )
                    error_list.append(cur_error)

        return error_list

    def _post_processing_error(self, error_list: List[Dict[str, Any]],
                               ) -> List[TopologyFeatureData]:

        return super()._post_processing_error(error_list=error_list)

    def _compatible_geometry_types(self) -> List[int]:

        return [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon, ]
