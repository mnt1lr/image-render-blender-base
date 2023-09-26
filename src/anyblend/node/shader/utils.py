#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /utils.py
# Created Date: Thursday, October 22nd 2020, 2:51:33 pm
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
import numbers

from typing import NamedTuple, Any, Union
from dataclasses import dataclass
from enum import Enum

from anybase.cls_any_error import CAnyError_Message


# #########################################################################
# Enum for Attribute node
class EAttributeType(str, Enum):
    GEOMETRY = "GEOMETRY"
    OBJECT = "OBJECT"
    INSTANCER = "INSTANCER"
    VIEW_LAYER = "VIEW_LAYER"


# endenum


# #########################################################################
# Base class for node socket collection declarations.
# This can be used to define inputs and outputs of node groups
@dataclass(frozen=True)
class CNodeSocketCollection:
    pass


# endclass


# #########################################################################
# Node socket info class to describe a node group input or output socket
class CNodeSocketInfo(NamedTuple):
    sName: str
    typSocket: bpy.types.NodeSocket
    xValue: Any


# endclass


@dataclass
class CNodeDescriptor:
    sTypeId: str
    sTypeName: str
    xNodeInput: Union[int, str]
    xNodeOutput: Union[int, str]


# endclass


###################################################################
def ReplaceNodeType(
    _xSNT: bpy.types.NodeTree,
    *,
    _xSearch: CNodeDescriptor,
    _xReplace: CNodeDescriptor,
    _bRecurse: bool = True,
):
    lReplaceNodes: list = []

    for ndX in _xSNT.nodes:
        if ndX.type == "GROUP" and _bRecurse is True:
            ReplaceNodeType(
                ndX.node_tree,
                _xSearch=_xSearch,
                _xReplace=_xReplace,
                _bRecurse=True,
            )

        elif ndX.type == _xSearch.sTypeId:
            lReplaceNodes.append(ndX)
        # endif
    # endfor

    for ndX in lReplaceNodes:
        ndReplace = _xSNT.nodes.new(_xReplace.sTypeName)
        for lnkX in ndX.inputs[_xSearch.xNodeInput].links:
            _xSNT.links.new(lnkX.from_socket, ndReplace.inputs[_xReplace.xNodeInput])
        # endfor
        for lnkX in ndX.outputs[_xSearch.xNodeOutput].links:
            _xSNT.links.new(ndReplace.outputs[_xReplace.xNodeOutput], lnkX.to_socket)
        # endfor
        _xSNT.nodes.remove(ndX)
    # endfor


# enddef


###################################################################
# Connect sockets or values with sockets
def _ConnectWithSocket(xSNT: bpy.types.NodeTree, xTrg: bpy.types.NodeSocket, xSrc: TData):
    if xSrc is not None:
        if isinstance(xSrc, numbers.Real):
            xTrg.default_value = xSrc
        elif isinstance(xSrc, tuple):
            xTrg.default_value = xSrc
        else:
            xSNT.links.new(xSrc, xTrg)
        # endif
    # endif


# enddef


###################################################################
def _ProvideNodeTreeInputSocket(ntGrp: bpy.types.NodeTree, sName: str, sTypeName: str, xValue: Any):
    if ntGrp.inputs.get(sName) is None:
        ntGrp.inputs.new(sTypeName, sName)
    # endif

    try:
        if hasattr(ntGrp.inputs[sName], "default_value"):
            ntGrp.inputs[sName].default_value = xValue
        # endif
    except Exception as xEx:
        raise CAnyError_Message(sMsg=f"Error setting default value of '{sName}' to '{xValue}'", xChildEx=xEx)
    # endtry


# enddef


###################################################################
def _ProvideNodeTreeOutputSocket(ntGrp: bpy.types.NodeTree, sName: str, sTypeName: str):
    if ntGrp.outputs.get(sName) is None:
        ntGrp.outputs.new(sTypeName, sName)
    # endif


# enddef


###################################################################
# Provide a shader node tree input
def ProvideNodeTreeInputs(
    ntGrp: bpy.types.NodeTree, xData: Union[list, CNodeSocketCollection]
) -> bpy.types.NodeGroupInput:
    if isinstance(xData, list):
        for lItem in xData:
            _ProvideNodeTreeInputSocket(ntGrp, lItem[0], lItem[1], lItem[2])
        # endfor

    elif isinstance(xData, CNodeSocketCollection):
        for xItem in vars(xData).values():
            if not isinstance(xItem, CNodeSocketInfo):
                raise CAnyError_Message(sMsg="CNodeSocketCollection object contains element of invalid type")
            # endif

            _ProvideNodeTreeInputSocket(ntGrp, xItem.sName, xItem.typSocket.__name__, xItem.xValue)
        # endfor
    else:
        raise CAnyError_Message(sMsg="Invalid input type of element 'xData'")
    # endif

    nodIn = ntGrp.nodes.get("Group Input")
    if nodIn is None:
        nodIn = ntGrp.nodes.new("NodeGroupInput")
    # endif

    return nodIn


# enddef


###################################################################
# Provide a shader node tree output
def ProvideNodeTreeOutputs(
    ntGrp: bpy.types.NodeTree, xData: Union[list, CNodeSocketCollection]
) -> bpy.types.NodeGroupOutput:
    if isinstance(xData, list):
        for lItem in xData:
            _ProvideNodeTreeOutputSocket(ntGrp, lItem[0], lItem[1])

        # endfor

    elif isinstance(xData, CNodeSocketCollection):
        for xItem in vars(xData).values():
            if not isinstance(xItem, CNodeSocketInfo):
                raise CAnyError_Message(sMsg="CNodeSocketCollection object contains element of invalid type")
            # endif

            _ProvideNodeTreeOutputSocket(ntGrp, xItem.sName, xItem.typSocket.__name__)
        # endfor
    else:
        raise CAnyError_Message(sMsg="Invalid input type of element 'xData'")
    # endif

    nodOut = ntGrp.nodes.get("Group Output")
    if nodOut is None:
        nodOut = ntGrp.nodes.new("NodeGroupOutput")
    # endif

    return nodOut


# enddef


###################################################################
# Add a Shader node Group
#
# xSNT: Shader Node Tree instance
# xNodeTree: Node Tree instance
#
def Group(xSNT: bpy.types.NodeTree, xNodeTree: bpy.types.NodeTree) -> bpy.types.ShaderNodeGroup:
    nodX = xSNT.nodes.new("ShaderNodeGroup")
    nodX.node_tree = xNodeTree
    nodX.width *= 2

    return nodX


# enddef


###################################################################
# Add shader node: Attribute
def Attribute(xSNT: bpy.types.NodeTree, _eType: EAttributeType, _sName: str) -> bpy.types.NodeOutputs:
    nodX = xSNT.nodes.new("ShaderNodeAttribute")
    nodX.attribute_type = _eType
    nodX.attribute_name = _sName

    return nodX.outputs


# enddef


###################################################################
# Add shader node: Vertex Color
def VertexColor(xSNT: bpy.types.NodeTree, _sLayerName: str) -> bpy.types.NodeOutputs:
    nodX = xSNT.nodes.new("ShaderNodeVertexColor")
    nodX.layer_name = _sLayerName
    nodX.width *= 2

    return nodX.outputs


# enddef


###################################################################
# Add shader node: Geometry
def Geometry(xSNT) -> bpy.types.NodeOutputs:
    nodX = xSNT.nodes.new("ShaderNodeNewGeometry")

    return nodX.outputs


# enddef

###################################################################
# Add shader node: Object Info


def ObjectInfo(xSNT) -> bpy.types.NodeOutputs:
    nodX = xSNT.nodes.new("ShaderNodeObjectInfo")

    return nodX.outputs


# enddef

###################################################################
# Add shader node: Object Info


def LightPath(xSNT) -> bpy.types.NodeOutputs:
    nodX = xSNT.nodes.new("ShaderNodeLightPath")

    return nodX.outputs


# enddef

###################################################################
# Add shader node: Material Output


def Material(xSNT) -> bpy.types.NodeInputs:
    nodX = xSNT.nodes.new("ShaderNodeOutputMaterial")

    return nodX.inputs


# enddef

###################################################################
# Add shader node: Value


def Value(xSNT: bpy.types.NodeTree, sTitle, fValue) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeValue")

    nodX.outputs[0].default_value = fValue
    nodX.label = sTitle
    nodX.width *= 2

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Camera Data


def CameraData(xSNT: bpy.types.NodeTree, sTitle) -> bpy.types.NodeOutputs:
    nodX = xSNT.nodes.new("ShaderNodeCameraData")

    nodX.label = sTitle

    return nodX.outputs


# enddef
