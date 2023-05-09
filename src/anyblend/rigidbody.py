#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \rigidbody.py
# Created Date: Thursday, November 10th 2022, 3:37:16 pm
# Created by: Christian Perwass (CR/AEC5)
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
import mathutils

from .cls_rigidbody_object_pars import CRigidBodyObjectPars


# ###############################################################################################################
def ProvideWorld(*, _scnX=None):
    """Ensure that a rigid body world exists in the current scene or given scene.
        If no rigid body world exists, one is created.

    Returns
    -------
    Rigid Body World Object
        The current active rigid body world.
    """

    if _scnX is None:
        xScene = bpy.context.scene
    else:
        xScene = _scnX
    # endif

    xRBW = xScene.rigidbody_world
    if xRBW is None:
        bpy.ops.rigidbody.world_add()
        xRBW = xScene.rigidbody_world
    # endif

    return xRBW


# enddef


# ###############################################################################################################
def RemoveWorld(*, _scnX=None):
    """Ensure that a rigid body world exists in the current scene or given scene.
        If no rigid body world exists, one is created.

    Returns
    -------
    Rigid Body World Object
        The current active rigid body world.
    """

    if _scnX is None:
        xScene = bpy.context.scene
    else:
        xScene = _scnX
    # endif

    xRBW = xScene.rigidbody_world
    if xRBW is not None:
        bpy.ops.rigidbody.world_remove()
    # endif


# enddef

# ###############################################################################################################
def BakeWorld(*, _scnX=None):

    if _scnX is None:
        xScene = bpy.context.scene
    else:
        xScene = _scnX
    # endif

    xRBW = xScene.rigidbody_world
    if xRBW is None:
        raise RuntimeError("Scene has no rigid body world")
    # endif

    xCtx = bpy.context.copy()
    xCtx["point_cache"] = xRBW.point_cache
    with bpy.context.temp_override(**xCtx):
        bpy.ops.ptcache.bake(bake=True)
    # endwith


# enddef

# ###############################################################################################################
def AddObject(_objX, *, _xContext=None) -> CRigidBodyObjectPars:

    if _xContext is None:
        xCtx = bpy.context
    else:
        xCtx = _xContext
    # endif
    xScene = xCtx.scene

    # Provide a rigid body world if none exists
    xRBW = ProvideWorld(_scnX=xScene)

    if xRBW.collection is not None and _objX.name in xRBW.collection.objects:
        return CRigidBodyObjectPars(_objX=_objX)
    # endif

    xTempCtx = xCtx.copy()
    xTempCtx["active_object"] = _objX
    xTempCtx["selected_objects"] = [_objX]
    xTempCtx["object"] = _objX

    with xCtx.temp_override(**xTempCtx):
        bpy.ops.rigidbody.objects_add()
    # endif

    return CRigidBodyObjectPars(_objX=_objX)


# enddef
