#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /vector_scale.py
# Created Date: Thursday, October 22nd 2020, 2:51:25 pm
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

##########################################################
# Function for scale vector group
import bpy
from .. import align as nalign
from .. import shader as nsh

##########################################################
# Create Scale Vector Group


def Create(bForce=False):
    """
    Create shader node group to scale a vector.
    Optional Parameters:
        Force: Renew node tree even if group already exists.
    """

    # Create the name for the sensor specs shade node tree
    sGrpName = "AnyCam.Vector.Scale"

    # Try to get ray splitter specification node group
    ngMain = bpy.data.node_groups.get(sGrpName)

    ####!!! Debug
    # bpy.data.node_groups.remove(ngMain)
    # ngMain = None
    ####!!!

    if ngMain is None:
        ngMain = bpy.data.node_groups.new(sGrpName, "ShaderNodeTree")
        bUpdate = True
    else:
        bUpdate = bForce
    # endif

    if bUpdate == True:
        tNodeSpace = (50, 25)

        # Remove all nodes that may be present
        for nod in ngMain.nodes:
            ngMain.nodes.remove(nod)
        # endfor

        sVector = "Vector"
        sFactor = "Factor"
        sVectorScaled = "Scaled Vector"

        # Define inputs
        lInputs = [
            [sVector, "NodeSocketVector", (0, 0, 0)],
            [sFactor, "NodeSocketFloat", 1.0],
        ]

        # Define Output
        lOutputs = [[sVectorScaled, "NodeSocketVector"]]

        # Add group inputs if necessary and set default values
        nodIn = nsh.utils.ProvideNodeTreeInputs(ngMain, lInputs)

        # Add group outputs if necessary
        nodOut = nsh.utils.ProvideNodeTreeOutputs(ngMain, lOutputs)

        nodIn.location = (0, 0)

        skVector = nodIn.outputs[sVector]
        skFactor = nodIn.outputs[sFactor]

        lXYZ = nsh.vector.SeparateXYZ(ngMain, "Vec Comps", skVector)
        nalign.Relative(nodIn, (1, 0), lXYZ[0], (0, 1), tNodeSpace)

        skScaleX = nsh.math.Multiply(ngMain, "Scale X", lXYZ[0], skFactor)
        skScaleY = nsh.math.Multiply(ngMain, "Scale Y", lXYZ[1], skFactor)
        skScaleZ = nsh.math.Multiply(ngMain, "Scale Z", lXYZ[2], skFactor)

        nalign.Relative(lXYZ[0], (1, 1), skScaleX, (0, 0), tNodeSpace)
        nalign.Relative(skScaleX, (0, 1), skScaleY, (0, 0), tNodeSpace)
        nalign.Relative(skScaleY, (0, 1), skScaleZ, (0, 0), tNodeSpace)

        skVectorScaled = nsh.vector.CombineXYZ(
            ngMain, "Scaled Vector", skScaleX, skScaleY, skScaleZ
        )
        nalign.Relative(skScaleX, (1, 0), skVectorScaled, (0, 0), tNodeSpace)

        nalign.Relative(skVectorScaled, (1, 0), nodOut, (0, 0), tNodeSpace)
        ngMain.links.new(skVectorScaled, nodOut.inputs[sVectorScaled])

    # endif

    return ngMain


# enddef
