"""
dr_intersection_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: contains an algorithm for finding intersecting polygons.
"""

from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes, QgsPointXY

from .dr_abstract_check import DRAbstractCheck
from ....help_tools.help_func import TopologyFeatureData, LineToPolygonData


class DRIntersectionLine(DRAbstractCheck):
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

        polygon_list = optional_param.polygon_features

        feature_geoms_copy = feature_geoms.copy()
        error_list = []

        ids = []
        points = []

        extreme_points = []
        for geom in feature_geoms:
            qgs_points_list = DRIntersectionLine._line_to_poitns(geom)
            for qgs_points in qgs_points_list:
                extreme_points.append(qgs_points[0])
                extreme_points.append(qgs_points[-1])

        # print(extreme_points[0])

        for x, geom1 in enumerate(feature_geoms):
            for y, geom2 in enumerate(feature_geoms_copy):
                if x != y:
                    res = geom1.intersection(geom2)
                    if res.type() == 0:
                        res = res.asMultiPoint() if res.isMultipart() else [res.asPoint()]
                        for point in res:
                            if point in extreme_points:
                                ids.append([feature_ids[feature_geoms.index(geom1)],
                                    feature_ids[feature_geoms.index(geom2)]])
                                points.append([point.x(), point.y()])

            del feature_geoms_copy[feature_geoms_copy.index(geom1)]

        for x, point1 in enumerate(points):
            result_ids = []
            result_feature = []
            ids11, ids12 = ids[x]
            for y, point2 in enumerate(points):
                ids21, ids22 = ids[y]
                if x != y:
                    if point1 == point2 and point:
                        if ids11 not in result_ids:
                            result_ids.append(ids11)
                            result_feature.append(features[feature_ids.index(ids11)])
                            result_feature.append(polygon_list[feature_ids.index(ids11)])
                        if ids12 not in result_ids:
                            result_ids.append(ids12)
                            result_feature.append(features[feature_ids.index(ids12)])
                            result_feature.append(polygon_list[feature_ids.index(ids12)])
                        if ids21 not in result_ids:
                            result_ids.append(ids21)
                            result_feature.append(features[feature_ids.index(ids21)])
                            result_feature.append(polygon_list[feature_ids.index(ids21)])
                        if ids22 not in result_ids:
                            result_ids.append(ids22)
                            result_feature.append(features[feature_ids.index(ids22)])
                            result_feature.append(polygon_list[feature_ids.index(ids22)])

            del points[0]

            if len(result_ids) == 0:
                result_ids = ids[x]
                result_feature.append(features[feature_ids.index(ids11)])
                result_feature.append(polygon_list[feature_ids.index(ids11)])
                result_feature.append(features[feature_ids.index(ids12)])
                result_feature.append(polygon_list[feature_ids.index(ids12)])

            meaning = f"{str(result_ids[1:])[1:-1]}"

            error = TopologyFeatureData(
                layer_name=layer_name,
                feature_id=str(result_ids[0]),
                error_type="Наименование ошибки",
                error_coordinate=QgsGeometry().fromPointXY(QgsPointXY(point1[0], point1[1])),
                feature_object=result_feature,
                meaning=meaning + f". Количество повторений: {len(result_ids) - 1}" if len(result_ids) > 2 else meaning,
                )
            error_list.append(error)

        # print(len(error_list))

        return error_list

    def _post_processing_error(self, error_list: Union[List[Dict[str, Any]],
    List[TopologyFeatureData]]) -> TopologyFeatureData:

        return super()._post_processing_error(error_list=error_list)

    def _compatible_geometry_types(self) -> List[int]:
        return [QgsWkbTypes.LineString, QgsWkbTypes.MultiLineString]

    @staticmethod
    def _line_to_poitns(geometry: QgsGeometry) -> List[List[float]]:
        
        points = []

        if geometry.isMultipart():
            points = geometry.asMultiPolyline()
        else:
            points = [geometry.asPolyline()]

        return points
