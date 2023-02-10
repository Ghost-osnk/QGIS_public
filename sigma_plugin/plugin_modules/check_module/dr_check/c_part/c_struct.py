"""
c_struct.py
Copyright (c) 2022, Digital Research.
Author: Ovsyannikov Vladimir - ovsyannikov.vs@dclouds.ru.

This Library is not free software; it is made to order for "Рослесинфорг".

File description: contains model-classes; analog structure on c.
DRPointStruct description: contains fields for storing point coordinates.
DRSelfErrorStruct description: contains fields for storing information about found error.
DRGeometryStruct description: contains fields for storing information about QgsGeometry type.
"""

import ctypes


class DRPointStruct(ctypes.Structure):
    """This class contains fields for storing point coordinates."""

    _fields_ = [('x', ctypes.c_double),
                ('y', ctypes.c_double)]


class DRSelfErrorStruct(ctypes.Structure):
    """This class contains fields for storing information about found error."""

    _fields_ = [('feature_id', ctypes.c_int64),
                ('x', ctypes.c_int64),
                ('y', ctypes.c_int64)]


class DRGeometryStruct(ctypes.Structure):
    """This class contains fields for storing information about QgsGeometry type."""

    _fields_ = [('vertices', ctypes.POINTER(DRPointStruct)),
                ('count_vertices', ctypes.c_int),
                ('feat_id', ctypes.c_int64)]
