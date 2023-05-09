#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \blend\color.py
# Created Date: Monday, September 20th 2021, 3:21:30 pm
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
import math
import numpy as np


def ConvertHsvToRgb(tHsv):

    fH = math.fmod(tHsv[0], 360.0)
    fC = tHsv[1] * tHsv[2]
    fX = fC * (1.0 - math.fabs(math.fmod(fH / 60.0, 2.0) - 1.0))
    fM = tHsv[2] - fC

    if fH >= 0.0 and fH < 60.0:
        tRgb = (fC, fX, 0.0)
    elif fH < 120.0:
        tRgb = (fX, fC, 0.0)
    elif fH < 180.0:
        tRgb = (0.0, fC, fX)
    elif fH < 240.0:
        tRgb = (0.0, fX, fC)
    elif fH < 300.0:
        tRgb = (fX, 0.0, fC)
    else:
        tRgb = (fC, 0.0, fX)
    # endif

    tRgb = tuple((x + fM for x in tRgb))
    return tRgb


# endif


def _ConvRgbLinToS(fValue):
    if fValue <= 0.0031308:
        return fValue * 12.92
    else:
        return 1.055 * math.pow(fValue, 1.0 / 2.4) - 0.055
    # endif


# enddef


def ConvertRgbLinearToS(xData):

    if isinstance(xData, float):
        return _ConvRgbLinToS(xData)

    elif isinstance(xData, tuple):
        if len(xData) < 3:
            raise Exception("Color tuple must have at least 3 components")
        # endif

        return (
            _ConvRgbLinToS(xData[0]),
            _ConvRgbLinToS(xData[1]),
            _ConvRgbLinToS(xData[2]),
        )

    elif isinstance(xData, list):
        xNewData = []
        # expect list of iterables with at least 3 components
        for xCol in xData:
            xNewData.append(
                (
                    _ConvRgbLinToS(xCol[0]),
                    _ConvRgbLinToS(xCol[1]),
                    _ConvRgbLinToS(xCol[2]),
                )
            )
        # endfor
        return xNewData

    elif isinstance(xData, np.ndarray):
        return np.where(
            xData <= 0.0031308, xData * 12.92, 1.055 * np.pow(xData, 1 / 2.4) - 0.055
        )

    else:
        raise Exception("Unsupported data type for conversion")
    # endif


# enddef
