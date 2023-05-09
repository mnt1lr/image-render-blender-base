#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \material\cls_material.py
# Created Date: Tuesday, May 4th 2021, 8:06:50 am
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
from typing import Union


class CMaterial:
    def __init__(self, sName="Unnamed", bForce=False):

        self._bNeedUpdate: bool = False
        self.matX: bpy.types.Material = bpy.data.materials.get(sName)

        if self.matX is not None and bForce:
            bpy.data.materials.remove(self.matX)
            self.matX = None
        # endif

        # Create material if it is not available
        if self.matX is None:
            self._bNeedUpdate = True
            self.matX = bpy.data.materials.new(name=sName)
            self.matX.use_nodes = True
            self.matX.use_fake_user = False
        # endif

    # enddef

    @property
    def xMaterial(self) -> bpy.types.Material:
        return self.matX

    # enddef

    @property
    def sName(self) -> str:
        return self.matX.name

    # enddef

    @property
    def xNodeTree(self) -> bpy.types.NodeTree:
        return self.matX.node_tree

    # enddef

    @property
    def xNodes(self) -> bpy.types.Nodes:
        return self.matX.node_tree.nodes

    # enddef

    @property
    def xLinks(self) -> bpy.types.NodeLinks:
        return self.matX.node_tree.links

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

    ################################################################
    # Set default color maps to base color of principled bsdf
    # This function should be overwritten by derived classes to
    # map to the material's specific base color node
    def SetColor(self, tColor: Union[list, tuple[float, float, float, float]]):

        if not (isinstance(tColor, tuple) or isinstance(tColor, list)) or len(tColor) != 4:
            raise Exception("Expect a 4-element tuple as parameter")
        # endif

        nodeBSDF: bpy.types.Node = self.xNodes.get("Principled BSDF")
        inBC: bpy.types.NodeSocketColor = nodeBSDF.inputs["Base Color"]
        inBC.default_value = tuple(tColor)

    # enddef

    ################################################################
    # Set default color maps to base color of principled bsdf
    # This function should be overwritten by derived classes to
    # map to the material's specific base color node
    def GetColor(self) -> tuple[float, float, float, float]:

        nodeBSDF: bpy.types.Node = self.xNodes.get("Principled BSDF")
        inBC: bpy.types.NodeSocketColor = nodeBSDF.inputs["Base Color"]
        return inBC.default_value

    # enddef


# endclass
