"""
dr_geometry_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

File description: contains two classes: "GeometryCheckType" and "DRGeometryCheck".
GeometryCheckType description: analog of enum on C.
DRGeometryCheck description: main class of geometry_check module.
"""

from typing import List
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import QgsGeometry, QgsWkbTypes

from .dr_hole_check import DRHoleCheck
from .dr_selfcontact_check import DRSelfContact
from .dr_inside_object_check import DRInsideObject
from .dr_overlap_polygon_check import DROverlapPolygon
from .dr_empty_geometry_check import DREmptyGeometry
from .dr_missing_vertex_check import DRMissingVertex
from .dr_duplicate_nodes_check import DRDuplicateNodes
from .dr_selfIntersection_check import DRSelfIntersection
from .dr_duplicate_geometry_check import DRDuplicateGeometry
from .dr_doubled_attributes_check import DRDoubledAttributesCheck
from .dr_geometry_validation_check import DRValidateGeometry

from ....help_tools.config_reader import ConfigWorker

class GeometryCheckType:
    """Type of checks."""

    checkGeomSelfIntersections = 0
    checkGeomSelfContact = 1
    checkGeomDuplicateVertex = 2
    checkGeomPolygonCountVertex = 3
    checkGeomHoleCheck = 4
    checkGeomDuplicateGeometry = 5
    checkGeomInsideObject = 6
    checkGeomOverlapPolygon = 7
    checkGeomEmptyGeometry = 8
    checkAtrrAddresses = 9
    checkGeomValidation = 10


class DRGeometryCheck:
    """Geometry Check class for unite all checks."""

    def __init__(
            self,
            layers_for_check: list,
            config: ConfigWorker,
            progress_bar: QProgressBar
    ) -> None:

        self.layers_for_check = layers_for_check
        self.config = config
        self.errors_features_list = []
        self.progress_bar = progress_bar

    def run_check(self, check_types: List[GeometryCheckType]):
        """Public function from which the execution of the class functionality begins."""

        error_point_list = [
            GeometryCheckType.checkGeomDuplicateGeometry,
            GeometryCheckType.checkGeomEmptyGeometry,
            GeometryCheckType.checkGeomValidation,
        ]

        error_line_list = [
            GeometryCheckType.checkGeomSelfIntersections,
            GeometryCheckType.checkGeomSelfContact,
            GeometryCheckType.checkGeomDuplicateVertex,
            GeometryCheckType.checkGeomDuplicateGeometry,
            GeometryCheckType.checkGeomEmptyGeometry,
            GeometryCheckType.checkGeomValidation,
        ]

        error_polygon_list = [
            GeometryCheckType.checkGeomSelfIntersections,
            GeometryCheckType.checkGeomSelfContact,
            GeometryCheckType.checkGeomDuplicateVertex,
            GeometryCheckType.checkGeomPolygonCountVertex,
            GeometryCheckType.checkGeomHoleCheck,
            GeometryCheckType.checkGeomDuplicateGeometry,
            GeometryCheckType.checkGeomInsideObject,
            GeometryCheckType.checkGeomOverlapPolygon,
            GeometryCheckType.checkGeomEmptyGeometry,
            GeometryCheckType.checkGeomValidation,
        ]

        for layer_for_check in self.layers_for_check:

            features = []
            feature_ids = []
            feature_geoms = []

            layer_name = layer_for_check.name()
            layer_features = layer_for_check.getFeatures()
            # print("layer_name:", layer_name)

            for feat in layer_features:
                features.append(feat)
                feature_ids.append(feat.id())
                feature_geoms.append(feat.geometry())

            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(len(check_types))
            self.progress_bar.show()

            geometry_type = None

            for geom in feature_geoms:
                if geom is not None:
                    geometry_type = geom.wkbType()
                    break

            if geometry_type is None:
                continue

            if geometry_type in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon,]:
                acces_check_type = error_polygon_list
            elif geometry_type in [QgsWkbTypes.LineString, QgsWkbTypes.MultiLineString,]:
                acces_check_type = error_line_list
            elif geometry_type in [QgsWkbTypes.Point, QgsWkbTypes.MultiPoint,]:
                acces_check_type = error_point_list
            else:
                continue

            for check_type in check_types:
                optional_param = None
                if check_type not in acces_check_type:
                    continue

                self.progress_bar.setValue(check_types.index(check_type))
                checker = None
                if check_type == GeometryCheckType.checkGeomSelfIntersections:
                    checker = DRSelfIntersection()

                if check_type == GeometryCheckType.checkGeomSelfContact:
                    checker = DRSelfContact()

                elif check_type == GeometryCheckType.checkGeomDuplicateVertex:
                    checker = DRDuplicateNodes()

                elif check_type == GeometryCheckType.checkGeomValidation:
                    checker = DRValidateGeometry()

                elif check_type == GeometryCheckType.checkGeomPolygonCountVertex:
                    checker = DRMissingVertex()

                elif check_type == GeometryCheckType.checkGeomHoleCheck:
                    checker = DRHoleCheck()

                elif check_type == GeometryCheckType.checkGeomDuplicateGeometry:
                    checker = DRDuplicateGeometry()

                elif check_type == GeometryCheckType.checkGeomInsideObject:
                    checker = DRInsideObject()

                elif check_type == GeometryCheckType.checkGeomEmptyGeometry:
                    checker = DREmptyGeometry()

                elif check_type == GeometryCheckType.checkGeomOverlapPolygon:                    
                    checker = DROverlapPolygon()

                if checker:
                    self.errors_features_list.extend(
                        checker.run_check(layer_name, features, feature_ids, feature_geoms, optional_param=optional_param)
                    )

        if GeometryCheckType.checkAtrrAddresses in check_types:
            checker_attributes = DRDoubledAttributesCheck(
                config=self.config, layers=self.layers_for_check
            )
            self.errors_features_list.extend(
                checker_attributes.check_doubled_attributes()
            )

        self.progress_bar.hide()

        # if len(self.errors_features_list) != 0:
        #     for i in range(len(self.errors_features_list)):
        #         print(f"error_{i}: {self.errors_features_list[i]}")

        return self.errors_features_list
