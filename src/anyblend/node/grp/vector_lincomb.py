#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /vector_lincomb.py
# Created Date: Thursday, October 22nd 2020, 2:51:24 pm
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
# Function for linear combination vector group
import bpy
from .. import align as nalign
from .. import shader as nsh

##########################################################
# Create Linear Combination Vector Group


def Create2(bForce=False):
    """
    Create shader node group to calculate the linear combination of two vectors.
    Optional Parameters:
        Force: Renew node tree even if group already exists.
    """

    # Create the name for the sensor specs shade node tree
    sGrpName = "AnyCam.Vector.LinComb2"

    # Try to get ray splitter specification node group
    ngMain = bpy.data.node_groups.get(sGrpName)

    ####!!! Debug
    # if ngMain is not None:
    #     bpy.data.node_groups.remove(ngMain)
    #     ngMain = None
    # # endif
    # bForce = True
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

        sFacA = "Factor A"
        sFacB = "Factor B"
        sVecA = "Vector A"
        sVecB = "Vector B"
        sLinComb = "Linear Combination"

        # Define inputs
        lInputs = [
            [sFacA, "NodeSocketFloat", 1.0],
            [sFacB, "NodeSocketFloat", 1.0],
            [sVecA, "NodeSocketVector", (0, 0, 0)],
            [sVecB, "NodeSocketVector", (0, 0, 0)],
        ]

        # Define Output
        lOutputs = [[sLinComb, "NodeSocketVector"]]

        # Add group inputs if necessary and set default values
        nodIn = nsh.utils.ProvideNodeTreeInputs(ngMain, lInputs)

        # Add group outputs if necessary
        nodOut = nsh.utils.ProvideNodeTreeOutputs(ngMain, lOutputs)

        nodIn.location = (0, 0)

        skVecA = nodIn.outputs[sVecA]
        skFacA = nodIn.outputs[sFacA]
        skVecB = nodIn.outputs[sVecB]
        skFacB = nodIn.outputs[sFacB]

        # Scale vector A
        skFacVecA = nsh.vector.Scale(ngMain, "Scaled Vec A", skVecA, skFacA)

        # Scale vector BaseException
        skFacVecB = nsh.vector.Scale(ngMain, "Scaled Vec B", skVecB, skFacB)

        # Add scaled vectors
        skLinComb = nsh.vector.Add(ngMain, "Linear Combination", skFacVecA, skFacVecB)

        # Link to outputs
        ngMain.links.new(skLinComb, nodOut.inputs[sLinComb])

        # Align nodes
        nalign.Relative(nodIn, (1, 0), skFacVecA, (0, 0.5), tNodeSpace)
        nalign.Relative(skFacVecA, (0, 1), skFacVecB, (0, 0), tNodeSpace)
        nalign.Relative(skFacVecA, (1, 0.5), skLinComb, (0, 0), tNodeSpace)
        nalign.Relative(skLinComb, (1, 0), nodOut, (0, 0), tNodeSpace)

    # endif

    return ngMain


# enddef
