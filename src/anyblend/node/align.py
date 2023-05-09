#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /align.py
# Created Date: Thursday, October 22nd 2020, 2:51:20 pm
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

#################################################################
# Node Align Module v1.0
#################################################################
import bpy

#################################################################
# Set position of new node to the right of given node
def SetNodePosToRightOf(nodOrig, nodNew, tSpacing):

    tLoc = nodOrig.location
    nodNew.location = (tLoc[0] + nodOrig.width + tSpacing[0], tLoc[1])


# enddef

#################################################################
# Set position of new node to the left of given node
def SetNodePosToLeftOf(nodOrig, nodNew, tSpacing):

    tLoc = nodOrig.location
    nodNew.location = (tLoc[0] - nodNew.width - tSpacing[0], tLoc[1])


# enddef

#################################################################
# Set position of new node to below the given node
def SetNodePosToAboveOf(nodOrig, nodNew, tSpacing):

    tLoc = nodOrig.location
    iH = len(nodNew.inputs) * 25

    nodNew.location = (tLoc[0], tLoc[1] + nodNew.height + iH + tSpacing[1])


# enddef

#################################################################
# Set position of new node above of the given node
def SetNodePosToBelowOf(nodOrig, nodNew, tSpacing):

    tLoc = nodOrig.location
    iH = len(nodOrig.inputs) * 25

    nodNew.location = (tLoc[0], tLoc[1] - nodOrig.height - iH - tSpacing[1])


# enddef

#################################################################
# Align Node
def Relative(xOrig, tOrigRelPos, xAlign, tAlignRelPos, tSpacing):

    if isinstance(xOrig, bpy.types.NodeSocket):
        nodOrig = xOrig.node
    elif isinstance(xOrig, bpy.types.bpy_prop_collection):
        nodOrig = xOrig[0].node
    else:
        nodOrig = xOrig
    # endif

    if isinstance(xAlign, bpy.types.NodeSocket):
        nodAlign = xAlign.node
    elif isinstance(xAlign, bpy.types.bpy_prop_collection):
        nodAlign = xAlign[0].node
    else:
        nodAlign = xAlign
    # endif

    tOrigLoc = (nodOrig.location[0] - tSpacing[0], nodOrig.location[1] + tSpacing[1])

    iOrigSkCnt = len(nodOrig.inputs) + len(nodOrig.outputs)
    iAlignSkCnt = len(nodAlign.inputs) + len(nodAlign.outputs)

    tOrigSize = (
        nodOrig.width + 2 * tSpacing[0],
        nodOrig.height + iOrigSkCnt * 10 + 2 * tSpacing[1],
    )
    tAlignSize = (
        nodAlign.width + 2 * tSpacing[0],
        nodAlign.height + iAlignSkCnt * 10 + 2 * tSpacing[1],
    )

    tAlignLoc = (
        tOrigLoc[0] + tOrigRelPos[0] * tOrigSize[0] - tAlignRelPos[0] * tAlignSize[0],
        tOrigLoc[1] - tOrigRelPos[1] * tOrigSize[1] + tAlignRelPos[1] * tAlignSize[1],
    )

    nodAlign.location = (tAlignLoc[0] + tSpacing[0], tAlignLoc[1] - tSpacing[1])


# enddef
