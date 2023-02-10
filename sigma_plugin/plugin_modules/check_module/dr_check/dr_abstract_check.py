"""
dr_abstract_check.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

Class description: Abstract class for dr_geometry_check module (main part).
"""

from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes

from ....help_tools.help_func import TopologyFeatureData


class DRAbstractCheck(ABC):
    """Abstract class for dr_geometry_check module (main part)"""

    def __init__(self):
        self._layer_name = None
        self._features = None
        self._feature_ids = None
        self._feature_geoms = None
        self.optional_param = None

    @abstractmethod
    def run_check(
        self,
        layer_name: str,
        features: List[QgsFeature],
        feature_ids: List[int],
        feature_geoms: List[QgsGeometry],
        optional_param: Any = None,
        ) -> List[TopologyFeatureData]:
        
        """Public function from which the execution of the class functionality begins."""

        if len(features) == 0:
            raise Exception("QgsFeature Does not exist")
        self._is_compatible(cur_geom=feature_geoms[0])
        self._layer_name = layer_name
        self._features = features.copy()
        self._feature_ids = feature_ids.copy()
        self._feature_geoms = feature_geoms.copy()
        self.optional_param = optional_param

        error_list = self._run_check(
            layer_name=self._layer_name,
            features=self._features,
            feature_ids=self._feature_ids,
            feature_geoms=self._feature_geoms,
            optional_param=self.optional_param,
        )
        return self._post_processing_error(error_list=error_list)

    @abstractmethod
    def _run_check(self, layer_name: str, features: List[QgsFeature],
                   feature_ids: List[int], feature_geoms: List[QgsGeometry],
                   optional_param: Any = None, ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def _post_processing_error(self, error_list: Union[List[Dict[str, Any]],
    List[TopologyFeatureData]]) -> List[TopologyFeatureData]:

        del self._layer_name
        del self._features
        del self._feature_ids
        del self._feature_geoms
        if error_list is None or len(error_list) == 0:
            return []
        elif isinstance(error_list[0], TopologyFeatureData):
            return error_list

        result_list = []

        for old_error in error_list:
            old_error_keys = old_error.keys()
            new_error = TopologyFeatureData(
                layer_name=old_error["layer_name"] if "layer_name" in old_error_keys else '',
                feature_id=old_error["feature_id"] if "feature_id" in old_error_keys else '',
                error_type=old_error["error_type"] if "error_type" in old_error_keys else '',
                feature_object=old_error["feature_object"] if "feature_object" in old_error_keys else None,
                error_coordinate=old_error["error_coordinate"] if "error_coordinate" in old_error_keys else None,
                meaning=old_error["meaning"] if "meaning" in old_error_keys else '',
                error_fixing=old_error["error_fixing"] if "error_fixing" in old_error_keys else '',
            )
            result_list.append(new_error)

        return result_list

    @abstractmethod
    def _compatible_geometry_types(self) -> List[int]:
        pass

    def _is_compatible(self, cur_geom: QgsGeometry) -> int:

        compatible_types = self._compatible_geometry_types()
        if not cur_geom.isEmpty() and cur_geom is not None:
            if cur_geom.type() + 1 in compatible_types:
                return cur_geom.type()
            else:
                type_names = ""
                for type_name in compatible_types:
                    type_names += f"{QgsWkbTypes.displayString(type_name)}, "
                raise Exception(
                    f"Неподдерживаемый тип данных.\nДоступные типы: {type_names[:-2]}."
                )
