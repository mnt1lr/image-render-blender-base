#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /color.py
# Created Date: Thursday, October 22nd 2020, 2:51:31 pm
# Author: Christian Perwass
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

###################################################################
# Module containing vector shader nodes
import bpy
from .types import TData

from . import utils as nutils

###################################################################
# Add shader node: Separate XYZ


def SeparateRGB(xSNT: bpy.types.NodeTree, sTitle: str, xColor: TData) -> bpy.types.NodeOutputs:

    nodX = xSNT.nodes.new("ShaderNodeSeparateRGB")
    nodX.label = sTitle

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xColor)

    return nodX.outputs


# enddef


###################################################################
# Add shader node: Separate XYZ
def CombineRGB(xSNT: bpy.types.NodeTree, sTitle: str, xR: TData, xG: TData, xB: TData) -> bpy.types.NodeOutputs:

    nodX = xSNT.nodes.new("ShaderNodeCombineRGB")
    nodX.label = sTitle

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xR)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xG)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[2], xB)

    return nodX.outputs


# enddef


###################################################################
# Add shader node: Separate XYZ
def BrightContrast(
    xSNT: bpy.types.NodeTree, sTitle: str, xColor: TData = None, xBright: TData = None, xContrast: TData = None
) -> bpy.types.NodeOutputs:

    nodX = xSNT.nodes.new("ShaderNodeBrightContrast")
    nodX.label = sTitle

    if xColor is not None:
        nutils._ConnectWithSocket(xSNT, nodX.inputs["Color"], xColor)
    # endif

    if xBright is not None:
        nutils._ConnectWithSocket(xSNT, nodX.inputs["Bright"], xBright)
    # endif

    if xContrast is not None:
        nutils._ConnectWithSocket(xSNT, nodX.inputs["Contrast"], xContrast)
    # endif

    return nodX.outputs


# enddef
