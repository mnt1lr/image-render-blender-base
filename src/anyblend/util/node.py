#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /util.py
# Created Date: Thursday, September 07 2021, 1:20:20 pm
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

import bpy

##############################################################
def GetByIdOrLabel(_xNodeTree, _sName):

    # Find node in material node tree, either by id or by label
    xNode = next((x for x in _xNodeTree.nodes if x.name == _sName), None)
    if xNode is None:
        xNode = next((x for x in _xNodeTree.nodes if x.label == _sName), None)
    # endif

    return xNode


# enddef


##############################################################
def GetByLabelOrId(_xNodeTree, _sName):

    # Find node in material node tree, either by label or id
    xNode = next((x for x in _xNodeTree.nodes if x.label == _sName), None)
    if xNode is None:
        xNode = next((x for x in _xNodeTree.nodes if x.name == _sName), None)
    # endif

    return xNode


# enddef


##############################################################
# Ensure that node groups of the given names do not have copies.
# Replace references to copies by references to the node group
# with the given name and remove the copy.
def MakeMaterialNodeGroupsUnique(_lNodeGroupNames):
    """Ensure that node groups of the given names do not have copies.
       Replace references to copies by references to the node group
       with the given name and remove the copy.

    Args:
        _lNodeGroupNames (list): List of node group base names (i.e. without a trailing '.001' etc.)

    Raises:
        RuntimeError: If node groups of the given names do not exist.
    """

    for sName in _lNodeGroupNames:
        if sName not in bpy.data.node_groups:
            raise RuntimeError("Node group '{}' does not exist".format(sName))
        # endif
    # endfor

    setRemoveNames = set()

    for matX in bpy.data.materials:
        if matX.node_tree is None:
            continue
        # endif

        for ndX in matX.node_tree.nodes:
            if ndX.type == "GROUP":
                for sName in _lNodeGroupNames:
                    sGrpName = ndX.node_tree.name
                    if sGrpName.startswith(sName) and sGrpName != sName:
                        ndX.node_tree = bpy.data.node_groups[sName]
                        setRemoveNames.add(sGrpName)
                    # endif
                # endfor node group names
            # endif of type group
        # endfor nodes
    # endfor materials

    for sName in setRemoveNames:
        # print("Removing node group '{}'".format(sName))
        bpy.data.node_groups.remove(bpy.data.node_groups[sName])
    # endfor


# enddef
