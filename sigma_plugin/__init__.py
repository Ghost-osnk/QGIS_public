# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Sigma
                                 A QGIS plugin
 Sigma plugin for Qgis.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-02-14
        copyright            : (C) 2022 by Dmitriev Pavel
        email                : dmitriev.pv@dclouds.ru
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
# from pathlib import Path
# import sys
#
# plugin_source_path = str(Path(__file__).parents[0])
#
# if plugin_source_path not in sys.path:
#     sys.path.append(str(Path(__file__).parents[0]))

from .sigma_plugin import Sigma

# TODO Перед релизом переделать на абсолюные импорты,
# TODO Не даёт перезапускать модули с помощью плагинрелоудера при абсолютных импортах.


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Sigma class from file Sigma.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    return Sigma(iface)