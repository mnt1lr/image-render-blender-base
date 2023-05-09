#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \util\convert.py
# Created Date: Saturday, February 19th 2022, 7:10:51 am
# Author: Christian Perwass (CR/AEC5)
# <LICENSE id="GPL-3.0">
#
#   Image-Render Blender base functions module
#   Copyright (C) 2022 Robert Bosch GmbH and its subsidiaries
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# </LICENSE>
###

import bpy


def MatrixToList(_matX):

    return [[fCol for fCol in xRow] for xRow in _matX]


# enddef


def MatrixToString(_matX, _sFormat="{:7.2f}"):

    return "\n".join([" ".join([_sFormat.format(fCol) for fCol in xRow]) for xRow in _matX])


# enddef


def BlenderUnitsPerMeterFactor(objScene=None):
    """Calculates the conversion factors between Meters and Blender Units for the scene passed.

    Parameters
    ----------
    objScene : _type_, Blender scene, if None passed use bpy.data.scenes["Scene"] as default

    Returns
    -------
    float
        Conversion Factor Meters to Blender Units
    """
    if objScene is None:
        objScene = bpy.data.scenes["Scene"]
    dicUnitsToMeters = {
        "METERS": 1,
        "KILOMETERS": 1000,
        "CENTIMETERS": 0.01,
        "MILLIMETERS": 0.001,
        "MICROMETERS": 0.000001,
    }
    # Nach gründlichem Testen an neuer Datei hat sich gezeigt dass die Einheit von Blender schon in der scale_length verarbeitet wird.
    # Kann jetzt auch nicht mehr nachvollziehen warum wir da zu anderem Ergebnis gekommen waren.
    fFactor: float = 1.0 / objScene.unit_settings.scale_length
    return fFactor


# enddef
