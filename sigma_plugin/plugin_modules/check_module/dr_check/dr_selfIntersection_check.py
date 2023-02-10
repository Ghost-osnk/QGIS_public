"""
dr_selfintersection_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm for finding geometries with self-intersection.
"""

import ctypes

from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsWkbTypes

from .c_part.c_struct import DRGeometryStruct, DRSelfErrorStruct
from .dr_abstract_check import DRAbstractCheck
from .c_part.dr_abstract_check_c import DRAbstractCheckC
from ....help_tools.help_func import TopologyFeatureData


class DRSelfIntersection(DRAbstractCheck, DRAbstractCheckC, ):
    """A class that contains an algorithm for finding geometries with self-intersection."""

    def __init__(self):
        super().__init__()
        self.__c_class = None
        self.__p_float_c_int_const = None
        self.__c_int_p_float_const = None

    def run_check(self, layer_name: str, features: List[QgsFeature],
        feature_ids: List[int], feature_geoms: List[QgsGeometry],
        optional_param: Any = None, ) -> List[TopologyFeatureData]:
        """Public function from which the execution of the class functionality begins."""

        self.__p_float_c_int_const = 1000000000000000
        self.__c_int_p_float_const = 1000000000000
        self.__c_class = super()._connect_c_bin("DRSelfIntersection",)
        self.__c_class.worker.restype = ctypes.POINTER(DRSelfErrorStruct)

        return super().run_check(layer_name=layer_name, features=features,
                                 feature_ids=feature_ids, feature_geoms=feature_geoms, )

    def _run_check(self, layer_name:str, features:List[QgsFeature],
        feature_ids:List[int], feature_geoms:List[QgsGeometry],
        optional_param: Any = None, ) -> List[TopologyFeatureData]:

        c_error_list = []

        compatible = super()._is_compatible(feature_geoms[0])
        points_dict, py_points, c_points = self._to_points(
            feature_geoms=feature_geoms,
            feature_ids=feature_ids,
            p_float_c_int_const=self.__p_float_c_int_const,
            compatible=compatible,
        )

        geoms_data = [(c_points[i], len(py_points[i]), list(points_dict.keys())[i])
                      for i in range(len(py_points))]
        count_errors = ctypes.c_int(0)
        count_geoms = ctypes.c_int(len(py_points))
        c_geoms = super()._list2array(DRGeometryStruct, len(py_points), geoms_data, )
        c_errors = super()._list2array(DRSelfErrorStruct, 2,
                                       (ctypes.c_int64(0), ctypes.c_int64(0), ctypes.c_int64(0)), )
        result_errors = self.__c_class.worker(ctypes.byref(c_geoms), count_geoms,
                                              ctypes.byref(c_errors), ctypes.byref(count_errors), )

        for i in range(count_errors.value):
            c_error_list.append([result_errors[i].feature_id,
                                 result_errors[i].x / self.__c_int_p_float_const,
                                 result_errors[i].y / self.__c_int_p_float_const])

        error_list = self._create_self_error(layer_name, features, feature_ids,
                                             "Самопересечение", c_error_list, )

        return error_list

    def _post_processing_error(self, error_list: Union[List[Dict[str, Any]],
    List[TopologyFeatureData]], ) -> List[TopologyFeatureData]:

        return super()._post_processing_error(error_list,)

    def _create_self_error(self, layer_name, features, feature_ids, error_type, init_error_list,):

        error_list = self._delete_repeating_error(init_error_list)

        return super()._create_self_error(layer_name, features, feature_ids,
                                          error_type, error_list, )

    def _compatible_geometry_types(self) -> List[int]:

        return [
            QgsWkbTypes.LineString,
            QgsWkbTypes.MultiLineString,
            QgsWkbTypes.Polygon,
            QgsWkbTypes.MultiPolygon,
        ]

    def _delete_repeating_error(self, init_error_list,):

        error_list = []
        count_list = [0 for i in range(0, len(init_error_list))]

        for error in init_error_list:
            if error not in error_list:
                error_list.append(error)
            else:
                count_list[error_list.index(error)] += 1

        for index, element in enumerate(count_list):
            if element > 1:
                error_list[index].append(int((element + 1) / 2))

        for error in error_list:
            error_coordinate=QgsGeometry.fromPointXY(QgsPointXY(error.error_coordinate[0],
                error.error_coordinate[1]))
            error.error_coordinate = error_coordinate

        return error_list
