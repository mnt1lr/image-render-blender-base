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
# save all label bone data

import re
import pyjson5 as json
from pathlib import Path

import bpy


def GetBoneData(*, sObject, sRegEx):

    reBone = re.compile(sRegEx)
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

    # loop over all bones in armature that match pattern
    # and store their data
    dicData = {}
    for bnX in armX.edit_bones:
        if not reBone.match(bnX.name):
            continue
        # endif

        matBone = bnX.matrix

        dicBone = dicData[bnX.name] = {
            "matrix": [[col for col in row] for row in matBone],
            "parent": bnX.parent.name,
            "layers": [x for x in bnX.layers],
        }

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

            dicBone[sAttribute] = getattr(bnX, sAttribute)
        # endfor

    # endfor bones

    # Switch object to object mode
    bpy.ops.object.mode_set(mode="OBJECT")

    return dicData


# enddef


dicData = GetBoneData(sObject="HG_Rig", sRegEx=r"AT\.Label;.+")

pathDir = Path(bpy.path.abspath("//"))
pathFile = pathDir / "Bones.json"

with open(pathFile.as_posix(), "w") as xFile:
    json.dump(dicData, xFile, indent=4)
# endwith

# print([x for x in dicData])
