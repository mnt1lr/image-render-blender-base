#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \_dev\SaveLabelBones_v1 copy.py
# Created Date: Tuesday, February 1st 2022, 11:47:33 am
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


# save all label bone data

import re
import pyjson5 as json
from pathlib import Path

import bpy
from mathutils import *


def SetBoneData(*, sObject, dicData, bOverwrite=True):

    objX = bpy.data.objects.get(sObject)
    if objX is None:
        raise RuntimeError(f"Object '{sObject}' not found")
    # endif

    if objX.type != "ARMATURE":
        raise RuntimeError(f"Object '{sObject}' is not an armature")
    # endif

    armX = objX.data

    # Switch to object mode
    bpy.ops.object.mode_set(mode="OBJECT")

    # Deselect all objects
    for objY in bpy.data.objects:
        objY.select_set(False)
    # endfor

    # Activate selected object
    bpy.context.view_layer.objects.active = objX

    # Switch object to edit mode
    bpy.ops.object.mode_set(mode="EDIT")

    bnsX = armX.edit_bones

    # loop over all bones in armature that match pattern
    # and store their data
    for sBone, dicBone in dicData.items():
        if sBone in bnsX:
            if bOverwrite is False:
                print(
                    f"Warning: bone '{sBone}' already present in armature '{objX.name}'"
                )
                continue
            else:
                bnX = bnsX[sBone]
            # endif
        else:
            bnX = bnsX.new(name=sBone)
        # endif

        sParent = dicBone["parent"]
        if isinstance(sParent, str):
            if sParent not in bnsX:
                print(
                    f"Warning: parent bone '{sParent}' of bone '{sBone}' not found. Omitting bone."
                )
                bnsX.remove(sBone)
                continue
            # endif

            bnX.parent = bnsX.get(sParent)
        # endif

        for iIdx, bLayer in enumerate(dicBone["layers"]):
            bnX.layers[iIdx] = bLayer
        # endfor

        lAttributes = [
            "length",
            "use_connect",
            "use_cyclic_offset",
            "use_deform",
            "use_endroll_as_inroll",
            "use_envelope_multiply",
            "use_inherit_rotation",
            "use_inherit_scale",
            "use_local_location",
            "use_relative_parent",
            "use_scale_easing",
            "inherit_scale",
            "envelope_distance",
            "envelope_weight",
            "head_radius",
            "tail_radius",
        ]

        for sAttribute in lAttributes:
            if not hasattr(bnX, sAttribute):
                print(f"Warning: Bone '{bnX.name}' has no attribute '{sAttribute}'")
                continue
            # endif

            setattr(bnX, sAttribute, dicBone[sAttribute])
        # endfor

        bnX.matrix = Matrix(dicBone["matrix"])

    # endfor bones

    # Switch object to object mode
    bpy.ops.object.mode_set(mode="OBJECT")


# enddef


pathDir = Path(bpy.path.abspath("//"))
pathFile = pathDir / "Bones.json"

with open(pathFile.as_posix(), "r") as xFile:
    dicData = json.load(xFile)
# endwith

SetBoneData(sObject="HG_Rig", dicData=dicData)


# print([x for x in dicData])
