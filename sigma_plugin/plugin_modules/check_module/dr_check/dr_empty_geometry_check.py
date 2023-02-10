"""
dr_empty_geometry_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm for finding empty geometry.
"""

from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes

from ....help_tools.help_func import TopologyFeatureData
from .dr_abstract_check import DRAbstractCheck


class DREmptyGeometry(DRAbstractCheck, ):
    """A class that contains an algorithm for finding empty geometry."""

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

        _error_list = []

        for index, geom in enumerate(feature_geoms):
            if geom.isEmpty():
                cur_error = TopologyFeatureData(
                    layer_name=layer_name,
                    feature_id=str(feature_ids[index]),
                    error_type="Гемеотрия отсутствует",
                    feature_object=features[index],
                )
                _error_list.append(cur_error)
        return _error_list

    def _post_processing_error(
            self,
            error_list: Union[List[Dict[str, Any]], List[TopologyFeatureData]],
    ) -> List[TopologyFeatureData]:

        return super()._post_processing_error(error_list=error_list, )

    def _compatible_geometry_types(self) -> List[int]:

        return [
            QgsWkbTypes.LineString,
            QgsWkbTypes.MultiLineString,
            QgsWkbTypes.Polygon,
            QgsWkbTypes.MultiPolygon,
            QgsWkbTypes.Point,
            QgsWkbTypes.MultiPoint
        ]
