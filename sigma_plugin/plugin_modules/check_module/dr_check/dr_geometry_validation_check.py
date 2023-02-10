"""Docstring"""

from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes

from .dr_abstract_check import DRAbstractCheck
from ....help_tools.help_func import TopologyFeatureData

class DRValidateGeometry(DRAbstractCheck):
    """asd"""
    def run_check(self, layer_name:str, features:List[QgsFeature],
        feature_ids:List[int], feature_geoms:List[QgsGeometry],
        optional_param: Any = None, ) -> List[TopologyFeatureData]:
        """Docstring"""

        return super().run_check(
            layer_name=layer_name,
            features=features,
            feature_ids=feature_ids,
            feature_geoms=feature_geoms,
        )

    def _run_check(self, layer_name:str, features:List[QgsFeature],
        feature_ids:List[int], feature_geoms:List[QgsGeometry],
        optional_param: Any = None, ) -> List[TopologyFeatureData]:
        """Docstring"""

        error_list = []

        for index, geom in enumerate(feature_geoms):
            if not (geom.isGeosValid() or geom.isNull()):
                error_list.append(
                    TopologyFeatureData(
                        layer_name=layer_name,
                        feature_id=str(feature_ids[index]),
                        feature_object=features[index],
                        error_type="Геометрия некорректна",
                    )
                )

        return error_list

    def _post_processing_error(
            self,
            error_list: Union[List[Dict[str, Any]], List[TopologyFeatureData]],
    ) -> List[TopologyFeatureData]:

        return super()._post_processing_error(error_list=error_list)

    def _compatible_geometry_types(self) -> List[int]:

        return [
            QgsWkbTypes.LineString,
            QgsWkbTypes.MultiLineString,
            QgsWkbTypes.Polygon,
            QgsWkbTypes.MultiPolygon,
            QgsWkbTypes.Point,
            QgsWkbTypes.MultiPoint
        ]
