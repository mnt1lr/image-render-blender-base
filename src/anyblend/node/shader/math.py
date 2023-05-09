#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /math.py
# Created Date: Thursday, October 22nd 2020, 2:51:32 pm
# Author: Christian Perwass
# <LICENSE id="GPL-3.0">
#
#   Image-Render Blender Camera add-on module
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

#######################################################
# Node Utility Functions
import bpy
from .types import TData

# from .. import align as nalign
from . import utils as nutils


###################################################################
# Add a Math shader node


def Absolute(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "ABSOLUTE"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node


def Add(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData, bClamp: bool = False) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "ADD"

    nodX.use_clamp = bClamp

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node


def Subtract(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData, bClamp: bool = False) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "SUBTRACT"

    nodX.use_clamp = bClamp

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node


def Multiply(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "MULTIPLY"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node


def Divide(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "DIVIDE"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node


def Modulo(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "MODULO"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node


def Power(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "POWER"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node
def Sign(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "SIGN"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef


def Sqrt(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "SQRT"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef


###################################################################
# Add a Math shader node
def Floor(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "FLOOR"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node


def IsLessThan(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "LESS_THAN"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node


def IsGreaterThan(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "GREATER_THAN"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node


def Sine(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, bClamp: bool = False) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "SINE"
    nodX.use_clamp = bClamp

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node


def Cosine(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, bClamp: bool = False) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "COSINE"
    nodX.use_clamp = bClamp

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add a Math shader node
def ArcCos(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, bClamp: bool = False) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "ARCCOSINE"
    nodX.use_clamp = bClamp

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef


###################################################################
# Add a Math shader node
def ArcTan2(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData, bClamp: bool = False) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "ARCTAN2"
    nodX.use_clamp = bClamp

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef


###################################################################
# Add a Math shader node
def Degrees(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, bClamp: bool = False) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "DEGREES"
    nodX.use_clamp = bClamp

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef


###################################################################
# Add a Math shader node
def Radians(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, bClamp: bool = False) -> bpy.types.NodeSocket:

    nodX = xSNT.nodes.new("ShaderNodeMath")
    nodX.operation = "RADIANS"
    nodX.use_clamp = bClamp

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Mix values
def MixFloat(
    xSNT: bpy.types.NodeTree,
    sTitle: str,
    xFactor: TData,
    xA: TData,
    xB: TData,
    bClampFactor: bool = True,
    bClampResult: bool = False,
) -> bpy.types.NodeSocket:

    if (3, 4, 0) > bpy.app.version:
        raise RuntimeError("You must use Blender version 3.4.0 or higher to use this feature")
    # endif

    nodX = xSNT.nodes.new("ShaderNodeMix")
    nodX.label = sTitle
    nodX.blend_type = "MIX"
    nodX.data_type = "FLOAT"
    nodX.clamp_factor = bClampFactor
    nodX.clamp_result = bClampResult

    nutils._ConnectWithSocket(xSNT, nodX.inputs["Factor"], xFactor)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["A"], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["B"], xB)

    return nodX.outputs[0]


# enddef


###################################################################
# Add a Math shader node


def MapRangeFloatLinear(
    xSNT: bpy.types.NodeTree,
    sTitle: str,
    xValue: TData,
    xFromMin: TData,
    xFromMax: TData,
    xToMin: TData,
    xToMax: TData,
    bClamp: bool = False,
) -> bpy.types.NodeSocket:

    nodX: bpy.types.ShaderNodeMapRange = xSNT.nodes.new("ShaderNodeMapRange")
    nodX.data_type = "FLOAT"
    nodX.interpolation_type = "LINEAR"
    nodX.clamp = bClamp

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xValue)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xFromMin)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[2], xFromMax)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[3], xToMin)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[4], xToMax)

    # Must not rename sockets. After saving and reloading blend file
    # sockets are automatically renamed to default and links vanish.
    # nodX.outputs[0].name = sTitle
    nodX.label = sTitle

    return nodX.outputs[0]


# enddef
