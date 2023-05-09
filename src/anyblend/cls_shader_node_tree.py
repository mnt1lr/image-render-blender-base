#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \material\cls_material.py
# Created Date: Tuesday, March 27th 2023, 8:06:50 am
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

import bpy


class CShaderNodeTree:
    def __init__(self, sName="Unnamed", bForce=False):

        self._bNeedUpdate: bool = False
        self._sntX: bpy.types.ShaderNodeTree = bpy.data.node_groups.get(sName)

        if self._sntX is not None and bForce:
            bpy.data.node_groups.remove(self._sntX)
            self._sntX = None
        # endif

        # Create material if it is not available
        if self._sntX is None:
            self._bNeedUpdate = True
            self._sntX = bpy.data.node_groups.new(name=sName, type="ShaderNodeTree")
            self._sntX.use_fake_user = False
        # endif

    # enddef

    @property
    def sName(self) -> str:
        return self._sntX.name

    # enddef

    @property
    def xNodeTree(self) -> bpy.types.ShaderNodeTree:
        return self._sntX

    # enddef

    @property
    def xNodes(self) -> bpy.types.Nodes:
        return self._sntX.nodes

    # enddef

    @property
    def xLinks(self) -> bpy.types.NodeLinks:
        return self._sntX.links

    # enddef

    def GetNode(self, _sName) -> bpy.types.Node:
        return self.xNodes.get(_sName)

    # enddef

    def RemoveNode(self, _sName):
        self.xNodes.remove(self.GetNode(_sName))

    # enddef

    def CreateLink(self, *, xOut, xIn) -> bpy.types.NodeLink:
        return self.xLinks.new(xIn, xOut)

    # enddef

    def Clear(self):
        for xNode in self.xNodes:
            self.xNodes.remove(xNode)
        # endfor

    # enddef


# endclass
