#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \incident_ray.py
# Created Date: Tuesday, March 23rd 2021, 4:58:28 pm
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

##########################################################
# Node group to calculate polynomial
import bpy
from anybase.cls_anyexcept import CAnyExcept
from .. import align as nalign
from .. import shader as nsh

from . import potentiate as modGrpPotentiate

##########################################################
# Create pixel fraction grid group


def Create(*, iCoefCnt, bForce=False):
    """
    Create shader node group to calculate a polynomial.
    Optional Parameters:
        Force: Renew node tree even if group already exists.
    """

    if iCoefCnt < 2:
        raise CAnyExcept("Polynomial must be of degree 1 or higher")
    # endif

    # Create the name for the sensor specs shade node tree
    sGrpName = "AnyCam.Polynomial.V2.deg{0:d}".format(iCoefCnt - 1)

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

        # Define inputs
        sValueIn = "Input"
        lCoefNames = ["Coef. {0:d}".format(i) for i in range(iCoefCnt)]

        lInputs = [
            [sValueIn, "NodeSocketFloat", 0.0],
        ]
        lInputs.extend(
            [[lCoefNames[i], "NodeSocketFloat", 0.0] for i in range(iCoefCnt)]
        )

        # Define Output
        sValueOut = "Output"

        lOutputs = [
            [sValueOut, "NodeSocketFloat"],
        ]

        # Add group inputs if necessary and set default values
        nodIn = nsh.utils.ProvideNodeTreeInputs(ngMain, lInputs)
        skX = nodIn.outputs[0]
        lskA = nodIn.outputs[1:]

        # Add group outputs if necessary
        nodOut = nsh.utils.ProvideNodeTreeOutputs(ngMain, lOutputs)

        nodIn.location = (-400, 0)

        # ###############################################################

        iPower = iCoefCnt - 1
        skMul = nsh.math.Multiply(
            ngMain, "a{0:d} * x".format(iPower), skX, lskA[iPower]
        )
        nalign.Relative(nodIn, (1, 1), skMul, (0, 0), tNodeSpace)

        skAdd = nsh.math.Add(
            ngMain,
            "p{0:d} = a{0:d} + a{1:d}*x".format(iPower - 1, iPower),
            lskA[iPower - 1],
            skMul,
        )
        nalign.Relative(skMul, (1, 0), skAdd, (0, 0), tNodeSpace)

        for iPower in range(iCoefCnt - 2, 0, -1):
            skMul_prev = skMul
            skMul = nsh.math.Multiply(ngMain, "p{0:d} * x".format(iPower), skX, skAdd)
            nalign.Relative(skMul_prev, (0, 0), skMul, (0, 1), tNodeSpace)

            skAdd = nsh.math.Add(
                ngMain,
                "p{0:d} = a{0:d} + p{1:d}*x".format(iPower - 1, iPower),
                skMul,
                lskA[iPower - 1],
            )
            nalign.Relative(skMul, (1, 0), skAdd, (0, 0), tNodeSpace)
        # endfor

        ngMain.links.new(skAdd, nodOut.inputs[0])
        nalign.Relative(skAdd, (1, 0), nodOut, (0, 0), tNodeSpace)

    # endif

    return ngMain


# enddef
