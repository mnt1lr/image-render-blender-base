#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /vector.py
# Created Date: Thursday, October 22nd 2020, 2:51:34 pm
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

###################################################################
# Module containing vector shader nodes
import bpy
from .types import TData

# from ..grp import vector_scale as GrpVecScale
from ..grp import vector_lincomb as GrpVecLinComb
from . import utils as nutils


###################################################################
# Add shader node: Separate XYZ
def SeparateXYZ(xSNT: bpy.types.NodeTree, sTitle: str, xVector: TData) -> bpy.types.NodeOutputs:
    nodX = xSNT.nodes.new("ShaderNodeSeparateXYZ")
    nodX.label = sTitle

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xVector)

    return nodX.outputs


# enddef


###################################################################
# Add shader node: Combine XYZ
def CombineXYZ(xSNT: bpy.types.NodeTree, sTitle: str, xX: TData, xY: TData, xZ: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeCombineXYZ")
    nodX.label = sTitle

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xX)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xY)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[2], xZ)

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Add vectors
def Add(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorMath")

    nodX.label = sTitle
    nodX.operation = "ADD"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    return nodX.outputs["Vector"]


# enddef


###################################################################
# Add shader node: Subtract vectors
def Subtract(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorMath")

    nodX.label = sTitle
    nodX.operation = "SUBTRACT"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    return nodX.outputs["Vector"]


# enddef


###################################################################
# Add shader node: Dot product
def Dot(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorMath")

    nodX.label = sTitle
    nodX.operation = "DOT_PRODUCT"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    return nodX.outputs["Value"]


# enddef


###################################################################
# Add shader node: Project
def Project(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xB: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorMath")

    nodX.label = sTitle
    nodX.operation = "PROJECT"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xB)

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Normalize
def Normalize(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorMath")

    nodX.label = sTitle
    nodX.operation = "NORMALIZE"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    return nodX.outputs["Vector"]


# enddef


###################################################################
# Add shader node: Normalize
def Length(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorMath")

    nodX.label = sTitle
    nodX.operation = "LENGTH"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)

    return nodX.outputs["Value"]


# enddef


###################################################################
# Add shader node: Transform vector from world to object coordinate system
# !! This converts a vector (i.e. a direction) not taking into account the object's origin.
def TransformWorldToObject(xSNT: bpy.types.NodeTree, sTitle: str, xVector: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorTransform")

    nodX.label = sTitle
    nodX.convert_from = "WORLD"
    nodX.convert_to = "OBJECT"
    nodX.vector_type = "VECTOR"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xVector)

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Transform vector from object to world coordinate system
# !! This converts a vector (i.e. a direction) not taking into account the object's origin.
def TransformObjectToWorld(xSNT: bpy.types.NodeTree, sTitle: str, xVector: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorTransform")

    nodX.label = sTitle
    nodX.convert_from = "OBJECT"
    nodX.convert_to = "WORLD"
    nodX.vector_type = "VECTOR"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xVector)

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Transform vector from world to object coordinate system
# !! This converts a vector (i.e. a direction) not taking into account the object's origin.
def TransformNormalWorldToObject(xSNT: bpy.types.NodeTree, sTitle: str, xVector: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorTransform")

    nodX.label = sTitle
    nodX.convert_from = "WORLD"
    nodX.convert_to = "OBJECT"
    nodX.vector_type = "NORMAL"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xVector)

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Transform vector from object to world coordinate system
# !! This converts a vector (i.e. a direction) not taking into account the object's origin.
def TransformNormalObjectToWorld(xSNT: bpy.types.NodeTree, sTitle: str, xVector: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorTransform")

    nodX.label = sTitle
    nodX.convert_from = "OBJECT"
    nodX.convert_to = "WORLD"
    nodX.vector_type = "NORMAL"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xVector)

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Transform vector from world to object coordinate system
# !! This converts a point, taking into account the object's origin.
def TransformPointWorldToObject(xSNT: bpy.types.NodeTree, sTitle: str, xVector: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorTransform")

    nodX.label = sTitle
    nodX.convert_from = "WORLD"
    nodX.convert_to = "OBJECT"
    nodX.vector_type = "POINT"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xVector)

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Transform vector from object to world coordinate system
# !! This converts a point, taking into account the object's origin.
def TransformPointObjectToWorld(xSNT: bpy.types.NodeTree, sTitle: str, xVector: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorTransform")

    nodX.label = sTitle
    nodX.convert_from = "OBJECT"
    nodX.convert_to = "WORLD"
    nodX.vector_type = "POINT"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xVector)

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Project
def Scale(xSNT: bpy.types.NodeTree, sTitle: str, xA: TData, xFactor: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeVectorMath")

    nodX.label = sTitle
    nodX.operation = "SCALE"

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["Scale"], xFactor)

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader group: Scale Vector
def LinComb2(
    xSNT: bpy.types.NodeTree, sTitle: str, xVecA: TData, xFacA: TData, xVecB: TData, xFacB: TData
) -> bpy.types.NodeSocket:
    ngVecLC = nutils.Group(xSNT, GrpVecLinComb.Create2())
    ngVecLC.label = sTitle

    nutils._ConnectWithSocket(xSNT, ngVecLC.inputs["Vector A"], xVecA)
    nutils._ConnectWithSocket(xSNT, ngVecLC.inputs["Vector B"], xVecB)

    nutils._ConnectWithSocket(xSNT, ngVecLC.inputs["Factor A"], xFacA)
    nutils._ConnectWithSocket(xSNT, ngVecLC.inputs["Factor B"], xFacB)

    return ngVecLC.outputs[0]


# enddef


###################################################################
# Add shader node: Normal Map
def NormalMap(xSNT: bpy.types.NodeTree, sTitle: str, xColor: TData, xStrength: TData = 1.0) -> bpy.types.NodeOutputs:
    nodX: bpy.types.ShaderNodeNormalMap = xSNT.nodes.new("ShaderNodeNormalMap")
    nodX.label = sTitle

    nutils._ConnectWithSocket(xSNT, nodX.inputs["Strength"], xStrength)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["Color"], xColor)

    return nodX.outputs


# enddef
