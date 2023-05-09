#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \types.py
# Created Date: Tuesday, January 17th 2023, 1:59:52 pm
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


from typing import Optional, Union, NamedTuple


# ########################################################################################################
# Mesh data. Can create a Blender object from this with 'from_pydata(lVex, lEdges, lFaces)' function.
class CMeshData(NamedTuple):
    lVex: list[tuple[float, float, float]]
    lEdges: list[list[int]]
    lFaces: list[list[int]]


# endclass
