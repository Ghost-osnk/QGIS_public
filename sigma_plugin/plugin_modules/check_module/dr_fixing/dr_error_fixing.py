"""
dr_error_fixing.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

File description: contains two classes: "DRFixingTypeList" and "DRErrorFixing".
DRFixingTypeList description: analog of enum on C.
DRErrorFixing description: main class of geometry_fixing module.
"""

from typing import List

from .dr_delete_nodes import DRDeleteNodes
from .dr_delete_geometry import DRDeleteGeometry


class DRFixingTypeList:
    """Type list of fixing type."""

    delete_nodes = 0
    delete_geometry = 1


class DRErrorFixing:
    """Geometry Check class for unite all fixing."""

    def __init__(self):

        self.__fix_error_list = []

    def run_fixing(self, fixing_types: List[DRFixingTypeList], fix_error_list: list):
        """Public function from which the execution of the class functionality begins."""

        for fixing_type in fixing_types:
            worker = None
            if fixing_type == DRFixingTypeList.delete_nodes:
                worker = DRDeleteNodes()
            elif fixing_type == DRFixingTypeList.delete_geometry:
                worker = DRDeleteGeometry()

            if worker:
                self.__fix_error_list.extend(worker.run_fixing(fix_error_list))

        return self.__fix_error_list
