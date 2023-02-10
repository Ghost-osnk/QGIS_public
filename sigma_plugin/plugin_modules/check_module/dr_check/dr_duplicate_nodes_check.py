"""contains the search functionality for duplicate vertices
dr_duplicate_nodes_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm for finding duplicate vertices.
"""

from collections import Counter
from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes, QgsPointXY

from .dr_abstract_check import DRAbstractCheck
from ....help_tools.help_func import TopologyFeatureData


class DRDuplicateNodes(DRAbstractCheck):
    """A class that contains an algorithm for finding duplicate vertices."""

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
        points_dict = self.__to_points(feature_geoms=feature_geoms, feature_ids=feature_ids)

        for feat_id in points_dict:
            repeat_points = []
            repeat_count = []
            for point, count in Counter(points_dict[feat_id][:-1]).items():
                if count > 1:
                    repeat_points.append(point)
                    repeat_count.append(count)

            for index, repeat_point in enumerate(repeat_points):
                find_indexes = [i for i, j in enumerate(points_dict[feat_id][:-1]) if j == repeat_point]
                for find_index in find_indexes:
                    if repeat_point == points_dict[feat_id][find_index + 1]:
                        # meaning = f"Количество дубликатов: {repeat_count[index] - 1}" if repeat_count[index] > 2 else ''
                        cur_error = TopologyFeatureData(
                            layer_name=layer_name,
                            feature_id=str(feat_id),
                            feature_object=features[feature_ids.index(feat_id)],
                            error_type="Дублирование вершины",
                            error_coordinate=QgsGeometry().fromPointXY(QgsPointXY(repeat_point)),
                            # meaning=meaning,
                        )
                        # print("cur_error:", cur_error)
                        error_list.append(cur_error)

        return error_list

    # def check_duplicate_error(self, error_list):
    #     coords = []
    #     fids = []

    #     for error in error_list:
    #         fids.append(int(error_list.feature_id))
    #         coords.append([error.error_coordinate.asPoint().x(), error.error_coordinate.asPoint().y()])

    #     print(coords)

    #     for i, coord in enumerate(coords):
    #         if error_list[i] is not None:
    #             find_indexes = [i for i, j in enumerate(coords) if j == coord]
    #             if len(find_indexes) != 1:
    #                 error_list[i].meaning = f"Количество дубликатов: {len(find_indexes)}"
    #                 find_indexes = find_indexes[1:]
    #                 for find_index in find_indexes:
    #                     error_list[find_index] = None
    #     result = []
    #     for error in error_list:
    #         if error is not None:
    #             result.append(error)

    #     return result


    def _post_processing_error(self, error_list: Union[List[Dict[str, Any]],
    List[TopologyFeatureData]]) -> TopologyFeatureData:
        # error_list = self.check_duplicate_error(error_list)
        return super()._post_processing_error(error_list=error_list)

    def _compatible_geometry_types(self) -> List[int]:

        return [QgsWkbTypes.LineString,
                QgsWkbTypes.MultiLineString,
                QgsWkbTypes.Polygon,
                QgsWkbTypes.MultiPolygon
                ]

    def __to_points(self, feature_geoms: List[QgsGeometry],
                    feature_ids: List[int]) -> Dict[int, List[QgsPointXY]]:

        compatible = super()._is_compatible(feature_geoms[0]) + 1
        points_dict = {}

        if compatible in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
            for index, geom in enumerate(feature_geoms):
                if not geom.isEmpty():
                    points_dict[feature_ids[index]] = geom.asMultiPolygon()[0][0]
        else:
            for index, geom in enumerate(feature_geoms):
                if not geom.isEmpty():
                    points_dict[feature_ids[index]] = geom.asMultiPolyline()[0]

        return points_dict
