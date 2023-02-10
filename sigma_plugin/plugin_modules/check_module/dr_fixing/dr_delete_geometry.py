"""
dr_delete_nodes.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm delete geometry.
"""

from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes, QgsPointXY

from ....help_tools.help_func import TopologyFeatureData, TopologyFixingData


class DRDeleteGeometry:
    """A class that contains an algorithm delete geometry."""

    def run_fixing(self, error_list,):
        """Public function from which the execution of the class functionality begins."""

        return self.__run_fixing(error_list=error_list)

    def __run_fixing(self, error_list):

        result_list = []

        for error in error_list:
            layer_name = error.layer_name
            feature = error.feature_object
            error_type = error.error_type

            feature.clearGeometry()

            result_list.append(
                TopologyFixingData(
                    layer_name=layer_name,
                    feature_object=feature,
                    error_type=error_type,
                    status=True
                )
            )

        return result_list

    def __compatible_geometry_types(self) -> List[int]:

        return [
            QgsWkbTypes.LineString,
            QgsWkbTypes.MultiLineString,
            QgsWkbTypes.Polygon,
            QgsWkbTypes.MultiPolygon,
            QgsWkbTypes.Point,
            QgsWkbTypes.MultiPoint
        ]

    def __is_compatible(self, cur_geom:QgsGeometry) -> int:
        compatible_types = self.__compatible_geometry_types()
        if cur_geom.type() + 1 in compatible_types:
            return cur_geom.type()

        else:
            raise Exception(
                "Неподдерживаемый тип данных.\nДоступные типы: Polygon, "
                "MultiPolygon, LineString, MultiLineString, Point, MultiPoint."
            )
