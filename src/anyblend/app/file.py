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

import bpy


def PackAllLocal():

    for clnX in bpy.data.collections:
        if clnX.library is not None:
            print("Making collection local: {}".format(clnX.name))
            clnX.id_data.make_local()
        # endif
    # endfor

    for objX in bpy.data.objects:
        if objX.library is not None:
            print("Making object local: {}".format(objX.name))
            objX.id_data.make_local()
        # endif
    # endfor

    for matX in bpy.data.materials:
        if matX.library is not None:
            print("Making material local: {}".format(matX.name))
            matX.id_data.make_local()
        # endif
    # endfor

    for ngX in bpy.data.node_groups:
        if ngX.library is not None:
            print("Making node group local: {}".format(ngX.name))
            ngX.id_data.make_local()
        # endif
    # endfor

    for imgX in bpy.data.images:
        if imgX.library is not None:
            print("Making image local: {}".format(imgX.name))
            imgX.id_data.make_local()
        # endif
    # endfor

    # Removing linked collections
    for clnX in bpy.data.collections:
        if clnX.library is not None:
            print("Removing collection: {}".format(clnX.name))
            bpy.data.collections.remove(clnX)
        # endif
    # endfor

    bpy.ops.file.pack_all()


# enddef


######################################################################
def IterUsers(_xElement):
    def UserTuple(_clnX):
        tResult = tuple(repr(x) for x in _clnX if x.user_of_id(_xElement))
        return tResult if len(tResult) > 0 else None

    # enddef

    return filter(
        None,
        (
            UserTuple(getattr(bpy.data, sProp))
            for sProp in dir(bpy.data)
            if isinstance(getattr(bpy.data, sProp, None), bpy.types.bpy_prop_collection)
        ),
    )


# enddef
