#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /vector_lincomb.py
# Created Date: Thursday, October 22nd 2020, 2:51:24 pm
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

##########################################################
# Function for linear combination vector group
import bpy
from .. import align as nalign
from .. import shader as nsh


##########################################################
# Create Linear Combination Vector Group
def Create(bForce=False):
    """
    Create shader node group to map an incoming ray to a given direction.
    Optional Parameters:
        Force: Renew node tree even if group already exists.
    """

    # Create the name for the sensor specs shade node tree
    sGrpName = "AnyCam.Bsdf.RayToDir.v2"

    # Try to get ray splitter specification node group
    ngMain = bpy.data.node_groups.get(sGrpName)

    # ###!!! Debug
    # if ngMain is not None:
    #     bpy.data.node_groups.remove(ngMain)
    #     ngMain = None
    # # endif
    # bForce = True
    # ###!!!

    if ngMain is None:
        ngMain = bpy.data.node_groups.new(sGrpName, "ShaderNodeTree")
        bUpdate = True
    else:
        bUpdate = bForce
    # endif

    if bUpdate is True:
        tNodeSpace = (50, 25)
        tNodeSpaceSmall = (25, 15)

        # Remove all nodes that may be present
        for nod in ngMain.nodes:
            ngMain.nodes.remove(nod)
        # endfor

        sIncoming = "Incoming (local)"
        sOutgoing = "Outgoing (local)"
        sVignettingCorrection = "Vignetting Correction"

        # Define inputs
        lInputs = [
            [sIncoming, "NodeSocketVector", (0, 0, 1)],
            [sOutgoing, "NodeSocketVector", (0, 0, 1)],
            [sVignettingCorrection, "NodeSocketColor", (1.0, 1.0, 1.0, 1.0)],
        ]

        sBSDF = "BSDF"

        # Define Output
        lOutputs = [[sBSDF, "NodeSocketShader"]]

        # Add group inputs if necessary and set default values
        nodIn = nsh.utils.ProvideNodeTreeInputs(ngMain, lInputs)

        # Add group outputs if necessary
        nodOut = nsh.utils.ProvideNodeTreeOutputs(ngMain, lOutputs)

        nodIn.location = (0, 0)

        skIncoming = nodIn.outputs[sIncoming]
        skOutgoing = nodIn.outputs[sOutgoing]
        skVignettingCorrection = nodIn.outputs[sVignettingCorrection]

        ######################################
        # Refract
        skFakeIOR = nsh.utils.Value(ngMain, "Fake IOR", 10.0)
        nalign.Relative(nodIn, (1, 1), skFakeIOR, (1, 0), tNodeSpaceSmall)

        skScaleInRay = nsh.vector.Scale(ngMain, "Scaled In. Ray", skIncoming, -1.0)
        nalign.Relative(skFakeIOR, (1, 0), skScaleInRay, (0, 1), tNodeSpace)

        skScaleOutRay = nsh.vector.Scale(
            ngMain, "Scaled Out. Ray", skOutgoing, skFakeIOR
        )
        nalign.Relative(skScaleInRay, (0, 1), skScaleOutRay, (0, 0), tNodeSpaceSmall)

        skScaledRefNorm = nsh.vector.Subtract(
            ngMain, "Scaled Ref. Norm.", skScaleInRay, skScaleOutRay
        )
        nalign.Relative(skScaleInRay, (1, 0), skScaledRefNorm, (0, 0), tNodeSpaceSmall)

        skRefNorm = nsh.vector.Normalize(ngMain, "Ref. Norm.", skScaledRefNorm)
        nalign.Relative(skScaledRefNorm, (1, 0), skRefNorm, (0, 0), tNodeSpaceSmall)

        skRefNormWorld = nsh.vector.TransformNormalObjectToWorld(
            ngMain, "Ref. Norm. (world)", skRefNorm
        )
        nalign.Relative(skRefNorm, (1, 0), skRefNormWorld, (0, 0), tNodeSpaceSmall)

        # Refract
        skBsdfRefract = nsh.bsdf.RefractionSharp(
            ngMain, "Refract Ray", skVignettingCorrection, skFakeIOR, skRefNormWorld
        )
        nalign.Relative(skRefNormWorld, (1, 0), skBsdfRefract, (0, 0), tNodeSpaceSmall)

        ######################################
        # Test whether to refract or reflect
        skCosA = nsh.vector.Dot(ngMain, "In . Out", skIncoming, skOutgoing)
        nalign.Relative(skScaleInRay, (0, 0), skCosA, (0, 1), tNodeSpace)

        skIsReflect = nsh.math.IsGreaterThan(ngMain, "Is Reflect", skCosA, -0.1)
        nalign.Relative(skBsdfRefract, (0, 0), skIsReflect, (0, 1), tNodeSpace)

        ######################################
        # Test whether outgoing ray is valid.
        # For example, if a target pixel is outside the imaging area of a lens,
        # the corresponding outgoing ray will have length zero.
        skOutLen = nsh.vector.Length(ngMain, "Out Ray Length", skOutgoing)
        nalign.Relative(skCosA, (0, 0), skOutLen, (0, 1), tNodeSpace)

        skIsValid = nsh.math.IsGreaterThan(ngMain, "Is Valid", skOutLen, 0.5)
        nalign.Relative(skOutLen, (1, 1), skIsValid, (0, 1), tNodeSpaceSmall)

        ######################################
        # Reflect
        skHalfAngleVec = nsh.vector.Add(
            ngMain, "Half angle vector", skIncoming, skOutgoing
        )
        nalign.Relative(skScaleOutRay, (0, 1), skHalfAngleVec, (0, 0), tNodeSpace)

        skReflectNorm = nsh.vector.Normalize(ngMain, "Reflect Normal", skHalfAngleVec)
        nalign.Relative(skHalfAngleVec, (1, 0), skReflectNorm, (0, 0), tNodeSpaceSmall)

        skReflectNormWorld = nsh.vector.TransformNormalObjectToWorld(
            ngMain, "Reflect Normal (world)", skReflectNorm
        )
        nalign.Relative(
            skReflectNorm, (1, 0), skReflectNormWorld, (0, 0), tNodeSpaceSmall
        )

        skBsdfReflect = nsh.bsdf.ReflectionSharp(
            ngMain, "Reflect Ray", skVignettingCorrection, skReflectNormWorld
        )
        nalign.Relative(skBsdfRefract, (0, 1), skBsdfReflect, (0, 0), tNodeSpace)

        ######################################
        # Mix Relflect and Refract
        skMix = nsh.bsdf.Mix(
            ngMain, "Final Ray", skIsReflect, skBsdfRefract, skBsdfReflect
        )
        nalign.Relative(skBsdfRefract, (1, 0), skMix, (0, 0), tNodeSpace)

        ######################################
        # Block invalid outgoing rays
        skBlack = nsh.bsdf.Transparent(ngMain, "Invalid Mask", (0, 0, 0, 1))
        nalign.Relative(skIsReflect, (1, 0), skBlack, (0, 0), tNodeSpace)

        skMask = nsh.bsdf.Mix(ngMain, "Masked Ray", skIsValid, skBlack, skMix)
        nalign.Relative(skBlack, (1, 0), skMask, (0, 1), tNodeSpace)

        ######################################
        # Group Output
        ngMain.links.new(skMask, nodOut.inputs[sBSDF])
        nalign.Relative(skMask, (1, 0), nodOut, (0, 0), tNodeSpaceSmall)
    # endif

    return ngMain


# enddef
