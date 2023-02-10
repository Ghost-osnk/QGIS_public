"""
dr_delete_nodes.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm delete nodes (vertices).
"""

from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes, QgsPointXY

from ....help_tools.help_func import TopologyFeatureData, TopologyFixingData


class DRDeleteNodes:
    """A class that contains an algorithm delete nodes (vertices)."""

    def run_fixing(self, error_list,):
        """Public function from which the execution of the class functionality begins."""

        return self.__run_fixing(error_list=error_list)

    def __run_fixing(self,error_list,):

        result_list = []

        for error in error_list:
            layer_name = error.layer_name
            feature = error.feature_object
            error_type = error.error_type
            error_coordinate = error.error_coordinate.asPoint()

            geom = feature.geometry()
            points = self.__to_points(geom)
            index_point = points.index(error_coordinate) + 1
            result = geom.deleteVertex(index_point)

            feature.setGeometry(geom)

            result_list.append(
                TopologyFixingData(
                    layer_name=layer_name,
                    feature_object=feature,
                    error_type=error_type,
                    status=result
                )
            )

        return result_list

    def __to_points(self, cur_geom:QgsGeometry) -> List[QgsPointXY]:

        compatible = self.__is_compatible(cur_geom) + 1

        points_list = list()

        if compatible:
            if compatible in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
                if not cur_geom.isEmpty():
                    points_list = cur_geom.asMultiPolygon()[0][0][1:-1]
            else:
                if not cur_geom.isEmpty():
                    points_list = cur_geom.asMultiPolyline()[0]

            return points_list

    def __compatible_geometry_types(self) -> List[int]:

        return [QgsWkbTypes.LineString,
                QgsWkbTypes.MultiLineString,
                QgsWkbTypes.Polygon,
                QgsWkbTypes.MultiPolygon
                ]

    def __is_compatible(self, cur_geom:QgsGeometry) -> int:

        compatible_types = self.__compatible_geometry_types()
        if cur_geom.type() + 1 in compatible_types:
            return cur_geom.type()

        else:
            raise Exception(
                "Неподдерживаемый тип данных.\nДоступные типы: Polygon, "
                "MultiPolygon, LineString, MultiLineString.")
