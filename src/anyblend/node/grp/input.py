#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \node\grp\empty.py
# Created Date: Tuesday, May 4th 2021, 9:47:17 am
# Author: Christian Perwass (CR/AEC5)
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

from anyblend.node import align as nalign
from anyblend.node import shader as nsh

###########################################################################
def Create(*, sName, lSockets, bForce=False):

    # try to get color input node group
    ngMain = bpy.data.node_groups.get(sName)

    bUpdate = False
    if ngMain is None:
        ngMain = bpy.data.node_groups.new(sName, "ShaderNodeTree")
        bUpdate = True
    else:
        bUpdate = bForce
    # endif

    if bUpdate:
        tNodeSpace = (50, 25)

        # Remove all nodes that may be present
        for nod in ngMain.nodes:
            ngMain.nodes.remove(nod)
        # endfor

        nodIn = nsh.utils.ProvideNodeTreeInputs(ngMain, lSockets)
        nodOut = nsh.utils.ProvideNodeTreeOutputs(ngMain, lSockets)
        nalign.Relative(nodIn, (1, 0), nodOut, (0, 0), tNodeSpace)

        ngMain.links.new(nodOut.inputs[0], nodIn.outputs[0])
    # endif

    return ngMain


# enddef
