"""
dr_selfcontact_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm for finding geometries with self-touch (selfcontact).
"""

import ctypes

from collections import Counter
from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsWkbTypes

from .c_part.c_struct import DRGeometryStruct, DRSelfErrorStruct
from .dr_abstract_check import DRAbstractCheck
from .c_part.dr_abstract_check_c import DRAbstractCheckC
from ....help_tools.help_func import TopologyFeatureData


class DRSelfContact(DRAbstractCheck, DRAbstractCheckC, ):
    """A class that contains an algorithm for finding geometries with self-touch (selfcontact)."""

    def __init__(self):
        super().__init__()
        self.__c_class = None
        self.__c_int_p_float_const = None
        self.__p_float_c_int_const = None

    def run_check(self, layer_name: str, features: List[QgsFeature],
                  feature_ids: List[int], feature_geoms: List[QgsGeometry],
                  optional_param: Any = None, ) -> List[TopologyFeatureData]:
        """Public function from which the execution of the class functionality begins."""

        self.__p_float_c_int_const = 1000000000000000
        self.__c_int_p_float_const = 1000000000000
        self.__c_class = super()._connect_c_bin("DRSelfContact", )
        self.__c_class.worker.restype = ctypes.POINTER(DRSelfErrorStruct)

        return super().run_check(layer_name=layer_name, features=features,
                                 feature_ids=feature_ids, feature_geoms=feature_geoms, )

    def _run_check(self, layer_name: str, features: List[QgsFeature],
                   feature_ids: List[int], feature_geoms: List[QgsGeometry],
                   optional_param: Any = None, ) -> List[TopologyFeatureData]:

        c_error_list = []

        compatible = super()._is_compatible(feature_geoms[0])
        points_dict, py_points, c_points = super()._to_points(
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

        error_list = self.__python_check(points_dict, c_error_list, )
        error_list = super()._create_self_error(layer_name, features, feature_ids,
                                                "Самоприкосновение", error_list, )
        error_list = self._delete_repeating_error(error_list)

        return error_list

    def _post_processing_error(self, error_list: List[Dict[str, Any]],
                               ) -> List[TopologyFeatureData]:

        return super()._post_processing_error(error_list, )

    def _compatible_geometry_types(self) -> List[int]:

        return [
            QgsWkbTypes.LineString, QgsWkbTypes.MultiLineString,
            QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon,
        ]

    def __get_indices(self, lst, element):
        return [i for i in range(len(lst)) if lst[i] == element]

    def __python_check(self, points_dict: Dict[int, List[Any]],
                       error_list: List[Union[int, float]], ) -> List[Dict[str, Any]]:
        for feat_id in points_dict:
            repeat_points = []
            repeat_count = []
            for point, count in Counter(points_dict[feat_id]).items():
                repeat_indices = self.__get_indices(points_dict[feat_id], point)
                if len(repeat_indices) > 1 and repeat_indices != [0, len(points_dict[feat_id]) - 1]:
                    if count > 1:
                        repeat_points.append(point)
                        repeat_count.append(count)

                    for repeat_point in repeat_points:
                        find_index = points_dict[feat_id].index(repeat_point)
                        if repeat_point != points_dict[feat_id][find_index + 1]:
                            error_list.append([feat_id, repeat_point.x(),
                                               repeat_point.y(), int(count)])

        return error_list

    def _delete_repeating_error(self, init_error_list, ):

        error_list = []

        for error in init_error_list:
            if error not in error_list:
                error_list.append(error)

        for error in error_list:
            error_coordinate = QgsGeometry.fromPointXY(QgsPointXY(error.error_coordinate[0],
                                                                  error.error_coordinate[1]))
            error.error_coordinate = error_coordinate

        return error_list
