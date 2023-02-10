"""
dr_abstract_check_c.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: Abstract class for dr_geometry_check module (c part).
"""


import os
import ctypes
import platform

from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Union
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY

from .c_struct import DRPointStruct
from .....help_tools.help_func import TopologyFeatureData

class DRAbstractCheckC(ABC):
    """Abstract class for dr_geometry_check module (c part)"""

    # @abstractmethod
    def _connect_c_bin(self, name: str):
        sigma_path = Path.absolute(Path(__file__).parents[0])
        system_bit = platform.architecture()[0].lower()
        system_name = platform.system().lower()
        c_bin_path = os.path.join(sigma_path, "bin")

        if "linux" in system_name:
            c_bin_path = os.path.join(c_bin_path, "Linux")
            name += ".so"
        elif "win" in system_name:
            c_bin_path = os.path.join(c_bin_path, "Windows")
            name += ".dll"
        else:
            c_bin_path = os.path.join(c_bin_path, "Darwin")

        if "64" in system_bit:
            c_bin_path = os.path.join(c_bin_path, "64")
        else:
            c_bin_path = os.path.join(c_bin_path, "32")

        full_path = os.path.join(c_bin_path, name)
        c_class = ctypes.CDLL(full_path)

        return c_class

    # @abstractmethod
    def _to_points(self, feature_geoms: QgsGeometry, feature_ids: List[int],
        p_float_c_int_const: int, compatible: int):

        points_dict = {}
        geom_points = []
        py_points = []
        for index, geom in enumerate(feature_geoms):

            if not geom.isEmpty():
                if compatible in [1, 4]:
                    points_dict[feature_ids[index]] = geom.asMultiPolyline()[0][:-1]

                    for qgs_point in geom.asMultiPolyline()[0]:
                        geom_points.append([qgs_point.x() * p_float_c_int_const,
                            qgs_point.y() * p_float_c_int_const])
                else:
                    points_dict[feature_ids[index]] = geom.asMultiPolygon()[0][0][:-1]

                    for qgs_point in geom.asMultiPolygon()[0][0]:
                        geom_points.append([qgs_point.x() * p_float_c_int_const,
                            qgs_point.y() * p_float_c_int_const])

                py_points.append(geom_points)
                geom_points = []

        array_type = DRPointStruct * len(py_points)
        result_type = ctypes.POINTER(DRPointStruct) * len(py_points)
        result = result_type()

        for i in range(len(py_points)):
            c_array = array_type()

            for j in range(len(py_points[i])):
                c_array[j] = DRPointStruct()
                c_array[j].x = py_points[i][j][0]
                c_array[j].y = py_points[i][j][1]

            result[i] = ctypes.cast(c_array, ctypes.POINTER(DRPointStruct))

        return points_dict, py_points, ctypes.cast(result,
                                                  ctypes.POINTER(ctypes.POINTER(DRPointStruct)))

    # @abstractmethod
    def _list2array(self, datatype, length: int, init_data):
        array_type = datatype * length
        array = array_type()

        if isinstance(init_data, tuple):
            array[0] = datatype(*init_data)

        elif isinstance(init_data, list):
            for index, element in enumerate(init_data):
                array[index] = datatype(*element)

        return ctypes.cast(array, ctypes.POINTER(datatype))

    # @abstractmethod
    def _create_self_error(self, layer_name: str, features: list[QgsFeature],
        feature_ids: List[int], error_type: str, init_error_list: List[Union[int, float]],):
        error_list = []

        for error in init_error_list:
            error_list.append(
                TopologyFeatureData(
                    layer_name=layer_name,
                    feature_id=str(error[0]),
                    error_type=error_type,
                    feature_object=features[feature_ids.index(error[0])],
                    error_coordinate=[error[1], error[2]],
                    meaning=f"Количество повторений: {error[3]}" if len(error) == 4 else "",
                )
            )

        return error_list
