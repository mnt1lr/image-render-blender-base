#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /bsdf.py
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

#######################################################
# Node BSDF Functions
import bpy
from .types import TData

# from .. import align as nalign
from . import utils as nutils
from ..grp import ray_to_dir_v2 as modGrpRayToDir


###################################################################
# Add shader node: Refraction


def RefractionSharp(
    xSNT: bpy.types.NodeTree, sTitle: str, xColor: TData, xIOR: TData, xNormal: TData
) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeBsdfRefraction")

    if bpy.app.version[0] > 3:
        nodX.distribution = "GGX"
    else:
        nodX.distribution = "SHARP"
    # endif

    nodX.inputs["Roughness"].default_value = 0.0

    nutils._ConnectWithSocket(xSNT, nodX.inputs["Color"], xColor)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["IOR"], xIOR)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["Normal"], xNormal)

    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add shader node: Refraction


def ReflectionSharp(xSNT: bpy.types.NodeTree, sTitle: str, xColor: TData, xNormal: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeBsdfGlossy")

    if bpy.app.version[0] > 3:
        nodX.distribution = "GGX"
    else:
        nodX.distribution = "SHARP"
    # endif

    nodX.inputs["Roughness"].default_value = 0.0

    nutils._ConnectWithSocket(xSNT, nodX.inputs["Color"], xColor)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["Normal"], xNormal)

    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add shader group: Scale Vector


def RayToDir(
    xSNT: bpy.types.NodeTree, sTitle: str, xIncoming: TData, xOutgoing: TData, xVignetting: TData = None
) -> bpy.types.NodeSocket:
    ngRef = nutils.Group(xSNT, modGrpRayToDir.Create())
    ngRef.label = sTitle

    nutils._ConnectWithSocket(xSNT, ngRef.inputs["Incoming (local)"], xIncoming)
    nutils._ConnectWithSocket(xSNT, ngRef.inputs["Outgoing (local)"], xOutgoing)
    if xVignetting is not None:
        nutils._ConnectWithSocket(xSNT, ngRef.inputs["Vignetting Correction"], xVignetting)
    # endif

    return ngRef.outputs[0]


# enddef

###################################################################
# Add shader node: Transparent


def Transparent(xSNT: bpy.types.NodeTree, sTitle: str, xColor: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeBsdfTransparent")

    nutils._ConnectWithSocket(xSNT, nodX.inputs["Color"], xColor)

    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add shader node: Emission


def Emission(xSNT: bpy.types.NodeTree, sTitle: str, xColor: TData, xStrength: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeEmission")

    nutils._ConnectWithSocket(xSNT, nodX.inputs["Color"], xColor)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["Strength"], xStrength)

    nodX.label = sTitle

    return nodX.outputs[0]


# enddef


###################################################################
# Add shader node: Emission
def Diffuse(
    xSNT: bpy.types.NodeTree, sTitle: str, xColor: TData, xRoughness: TData = 0.0, xNormal: TData = None
) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeBsdfDiffuse")

    nutils._ConnectWithSocket(xSNT, nodX.inputs["Color"], xColor)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["Roughness"], xRoughness)
    if xNormal is not None:
        nutils._ConnectWithSocket(xSNT, nodX.inputs["Normal"], xNormal)
    # endif

    nodX.label = sTitle

    return nodX.outputs[0]


# enddef

###################################################################
# Add shader node: Mix Shader


def Mix(xSNT: bpy.types.NodeTree, sTitle: str, xFactor: TData, xBsdfA: TData, xBsdfB: TData) -> bpy.types.NodeSocket:
    nodX = xSNT.nodes.new("ShaderNodeMixShader")

    nutils._ConnectWithSocket(xSNT, nodX.inputs[0], xFactor)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[1], xBsdfA)
    nutils._ConnectWithSocket(xSNT, nodX.inputs[2], xBsdfB)

    nodX.label = sTitle

    return nodX.outputs[0]


# enddef
