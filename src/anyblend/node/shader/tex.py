#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /tex.py
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

import bpy
from .types import TData
from enum import Enum

# from .. import align as nalign
from . import utils as nutils


class EExtension(str, Enum):
    REPEAT = "REPEAT"
    EXTEND = "EXTEND"
    CLIP = "CLIP"


# endclass


class EInterpolation(str, Enum):
    LINEAR = "Linear"
    CLOSEST = "Closest"
    CUBIC = "Cubic"
    SMART = "Smart"


# endclass


class EProjection(str, Enum):
    FLAT = "FLAT"
    BOX = "BOX"
    SPHERE = "SPHERE"
    TUBE = "TUBE"


# endclass


class EColorSpace(str, Enum):
    FILMIC_LOG = "Filmic Log"
    FILMIC_SRGB = "Filmic sRGB"
    LINEAR = "Linear"
    LINEAR_ACES = "Linear ACES"
    LINEAR_ACES_CG = "Linear ACEScg"
    NON_COLOR = "Non-Color"
    RAW = "Raw"
    SRGB = "sRGB"
    XYZ = "XYZ"


# endclass


class EAlphaMode(str, Enum):
    NONE = "NONE"
    STRAIGHT = "STRAIGHT"
    PRE_MULTIPLIED = "PREMUL"
    CHANNEL_PACKED = "CHANNEL_PACKED"


# endclass


###################################################################
# Add shader node: Noise Texture
def Noise(
    xSNT: bpy.types.NodeTree, sTitle: str, xVector: TData, xScale: TData, xDetail: TData, xDistortion: TData
) -> bpy.types.NodeOutputs:
    nodX = xSNT.nodes.new("ShaderNodeTexNoise")

    nutils._ConnectWithSocket(xSNT, nodX.inputs["Vector"], xVector)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["Scale"], xScale)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["Detail"], xDetail)
    nutils._ConnectWithSocket(xSNT, nodX.inputs["Distortion"], xDistortion)

    nodX.label = sTitle

    return nodX.outputs


# enddef


###################################################################
# Add shader node: Image Texture
def Image(
    xSNT: bpy.types.NodeTree,
    sTitle: str,
    xVector: TData,
    sImgName: str,
    *,
    eExtension: EExtension = EExtension.REPEAT,
    eInterpolation: EInterpolation = EInterpolation.LINEAR,
    eProjection: EProjection = EProjection.FLAT,
    eColorSpace: EColorSpace = EColorSpace.LINEAR,
    eAlphaMode: EAlphaMode = EAlphaMode.NONE,
) -> bpy.types.NodeOutputs:
    """Create an image texture node

    Parameters
    ----------
    xSNT : node group
        The node group this node is added to
    sTitle : str
        The title of the node
    xVector : vector
        The input vector to the texture
    sImgName : str
        Image name
    eExtension : EExtension, optional
        How the texture is extended at the borders. Default is EExtension.REPEAT
    eInterpolation : EInterpolation, optional
        Texture interpolation. Default is EInterpolation.LINEAR.
    eProjection : EProjection, optional
        Projection type of texture. Default is EProjection.FLAT.
    eColorSpace : EColorSpace, optional
        Color space of image. Default is EColorSpace.LINEAR
    eAlphaMode : EAlphaMode, optional
        Alpha mode of image. Default is EAlphaMode.NONE

    Returns
    -------
    node outputs
        The node output list that can be connected further

    Raises
    ------
    RuntimeError
        If the image of the given name is not found
    """
    nodX: bpy.types.ShaderNodeTexImage = xSNT.nodes.new("ShaderNodeTexImage")

    imgX = bpy.data.images.get(sImgName)
    if imgX is None:
        raise RuntimeError("Image '{}' not found".format(sImgName))
    # endif
    nodX.image = imgX
    nodX.extension = eExtension
    nodX.projection = eProjection
    nodX.interpolation = eInterpolation
    nodX.image.colorspace_settings.name = eColorSpace
    nodX.image.alpha_mode = eAlphaMode

    if xVector is not None:
        nutils._ConnectWithSocket(xSNT, nodX.inputs["Vector"], xVector)
    # endif

    nodX.label = sTitle

    return nodX.outputs


# enddef
