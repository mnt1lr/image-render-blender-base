#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \object_ops.py
# Created Date: Tuesday, December 6th 2022, 10:13:03 am
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

# import mathutils
import math
from pathlib import Path

# from . import collection
from . import viewlayer


######################################################
def _TempContextForObject(_objX: bpy.types.Object) -> bpy.types.Context:
    xCtx = bpy.context.copy()
    xCtx["object"] = _objX
    xCtx["active_object"] = _objX
    xCtx["selected_objects"] = [_objX]
    xCtx["selected_editable_objects"] = [_objX]

    return bpy.context.temp_override(**xCtx)


# enddef


######################################################
def SetOriginByType(_objX: bpy.types.Object, *, _sOriginType: str, _sCenter: str):
    with _TempContextForObject(_objX):
        setRes = bpy.ops.object.origin_set(type=_sOriginType, center=_sCenter)
        if setRes.pop() != "FINISHED":
            raise RuntimeError(f"Error setting origin of object '{_objX.name}'")
        # endif
    # endif

    viewlayer.Update()

    # vNewPos = _objX.location


# enddef


######################################################
def ApplyTransforms(
    _objX: bpy.types.Object,
    *,
    _bLocation: bool = True,
    _bRotation: bool = True,
    _bScale: bool = True,
    _bProperties: bool = True,
):
    with _TempContextForObject(_objX):
        setRes = bpy.ops.object.transform_apply(
            location=_bLocation, rotation=_bRotation, scale=_bScale, properties=_bProperties
        )
        if setRes.pop() != "FINISHED":
            raise RuntimeError(f"Error applying transformations to object '{_objX.name}'")
        # endif
    # endwith


# enddef


######################################################
def Duplicate(_objX: bpy.types.Object) -> bpy.types.Object:
    setObj: set[str] = set([x.name for x in bpy.data.objects])

    objDup: bpy.types.Object = None
    with _TempContextForObject(_objX):
        setRes = bpy.ops.object.duplicate()
        if setRes.pop() != "FINISHED":
            raise RuntimeError(f"Error duplicating object '{_objX.name}'")
        # endif
    # endwith

    objDup: bpy.types.Object = next((x for x in bpy.data.objects if x.name not in setObj), None)
    if objDup is None:
        raise RuntimeError(f"Error duplicating object '{_objX.name}'")
    # endif

    return objDup


# enddef


######################################################
def AddModifier(_objX: bpy.types.Object, _sModifier: str) -> bpy.types.Modifier:
    setMod: set[str] = set([x.name for x in _objX.modifiers])

    with _TempContextForObject(_objX):
        setRes = bpy.ops.object.modifier_add(type=_sModifier)
        if setRes.pop() != "FINISHED":
            raise RuntimeError(f"Error adding modifier '{_sModifier}' to object '{_objX.name}'")
        # endif
    # endwith

    modNew: bpy.types.Modifier = next((x for x in _objX.modifiers if x.name not in setMod), None)
    if modNew is None:
        raise RuntimeError(f"Error adding modifier '{_sModifier}' to object '{_objX.name}'")
    # endif

    return modNew


# enddef


######################################################
def AddModifier_Remesh(_objX: bpy.types.Object) -> bpy.types.RemeshModifier:
    return AddModifier(_objX, "REMESH")


# enddef


######################################################
def AddModifier_Shrinkwrap(_objX: bpy.types.Object) -> bpy.types.ShrinkwrapModifier:
    return AddModifier(_objX, "SHRINKWRAP")


# enddef


######################################################
def AddModifier_Smooth(_objX: bpy.types.Object) -> bpy.types.SmoothModifier:
    return AddModifier(_objX, "SMOOTH")


# enddef


######################################################
def AddModifier_MultiRes(_objX: bpy.types.Object) -> bpy.types.MultiresModifier:
    return AddModifier(_objX, "MULTIRES")


# enddef


######################################################
def ApplyModifier(_objX: bpy.types.Object, _modX: bpy.types.Modifier):
    if _modX.name not in _objX.modifiers:
        raise RuntimeError(f"Modifier '{_modX.name}' not part of object '{_objX.name}'")
    # endif

    with _TempContextForObject(_objX):
        setRes = bpy.ops.object.modifier_apply(modifier=_modX.name)
        if setRes.pop() != "FINISHED":
            raise RuntimeError(f"Error applying modifier '{_modX.name}' of object '{_objX.name}'")
        # endif
    # endwith


# enddef


######################################################
def DoMultiResSubdivide(
    _objX: bpy.types.Object, _modX: bpy.types.MultiresModifier, _iCount: int, *, _sMode: str = "CATMULL_CLARK"
):
    with _TempContextForObject(_objX):
        for iIdx in range(_iCount):
            bpy.ops.object.multires_subdivide(modifier=_modX.name, mode=_sMode)
        # endfor
    # endwith


# enddef


######################################################
def SetNewMaterial(
    _objX: bpy.types.Object,
    *,
    _sMaterialName: str = None,
    _bAppend: bool = False,
    _lBaseColor: list[float] = None,
    _lEmission: list[float] = None,
) -> bpy.types.Material:
    if not isinstance(_objX, bpy.types.Object):
        raise RuntimeError("Given element is no Blender object")
    # endif

    if _objX.data is None:
        raise RuntimeError(f"Object '{_objX.name}' has no 'data' block")
    # endif

    if not hasattr(_objX.data, "materials"):
        raise RuntimeError(f"Object '{_objX.name}' of type '{_objX.type}' has not materials")
    # endif

    setMat: set[str] = set([x.name for x in bpy.data.materials])

    with _TempContextForObject(_objX):
        setRes = bpy.ops.material.new()
        if setRes.pop() != "FINISHED":
            raise RuntimeError("Error creating new material")
        # endif
    # endwith

    matNew: bpy.types.Material = next((x for x in bpy.data.materials if x.name not in setMat), None)
    if matNew is None:
        raise RuntimeError("Error creating new material")
    # endif

    if isinstance(_sMaterialName, str):
        matNew.name = _sMaterialName
    # endif

    if len(_objX.data.materials) == 0 or _bAppend is True:
        _objX.data.materials.append(matNew)
    else:
        _objX.data.materials[0] = matNew
    # endif

    nodShader = matNew.node_tree.nodes.get("Principled BSDF")

    if isinstance(_lBaseColor, list):
        if len(_lBaseColor) < 3 or len(_lBaseColor) > 4:
            raise RuntimeError("Base color has to be list of 3 or 4 float components")
        # endif

        lColor = _lBaseColor.copy()
        if len(lColor) == 3:
            lColor.append(1.0)
        # endif

        if nodShader is not None:
            nodShader.inputs[0].default_value = lColor
        # endif
    # endif

    if isinstance(_lEmission, list):
        if len(_lEmission) < 3 or len(_lEmission) > 4:
            raise RuntimeError("Emission color has to be list of 3 or 4 float components")
        # endif

        lColor = _lEmission.copy()
        if len(lColor) == 3:
            lColor.append(1.0)
        # endif

        if nodShader is not None:
            nodShader.inputs["Emission"].default_value = lColor
        # endif
    # endif

    return matNew


# enddef


######################################################
def ImportToScene_Obj(_pathFile: Path) -> bpy.types.Object:
    xCtx = bpy.context.copy()

    objIn: bpy.types.Object
    with bpy.context.temp_override(**xCtx):
        # If an object is imported into a collection that is not visible in the current
        # view layer, it is not an element of 'bpy.context.selected_objects' after import.
        # Therefore, we store the names of all objects before import, and
        # then look for the one object that is not in that set, after import.
        setObj: set[str] = set([x.name for x in bpy.data.objects])

        setRes = bpy.ops.import_scene.obj(filepath=_pathFile.as_posix())
        # print(f"Importing '{(_pathFile.as_posix())}' -> {setRes}")
        if setRes.pop() != "FINISHED":
            raise RuntimeError(f"Error importing object from path: {(_pathFile.as_posix())}")
        # endif

        objIn: bpy.types.Object = next((x for x in bpy.data.objects if x.name not in setObj), None)
        if objIn is None:
            raise RuntimeError(f"Error importing object from path: {(_pathFile.as_posix())}")
        # endif
    # endwith

    viewlayer.Update()

    return objIn


# enddef


######################################################
def ImportToScene_Fbx(_pathFile: Path) -> bpy.types.Object:
    xCtx = bpy.context.copy()

    objIn: bpy.types.Object
    with bpy.context.temp_override(**xCtx):
        # If an object is imported into a collection that is not visible in the current
        # view layer, it is not an element of 'bpy.context.selected_objects' after import.
        # Therefore, we store the names of all objects before import, and
        # then look for the one object that is not in that set, after import.
        setObj: set[str] = set([x.name for x in bpy.data.objects])

        setRes = bpy.ops.import_scene.fbx(filepath=_pathFile.as_posix())
        # print(f"Importing '{(_pathFile.as_posix())}' -> {setRes}")
        if setRes.pop() != "FINISHED":
            raise RuntimeError(f"Error importing object from path: {(_pathFile.as_posix())}")
        # endif

        objIn: bpy.types.Object = next((x for x in bpy.data.objects if x.name not in setObj), None)
        if objIn is None:
            raise RuntimeError(f"Error importing object from path: {(_pathFile.as_posix())}")
        # endif
    # endwith

    viewlayer.Update()

    return objIn


# enddef


######################################################
def ExportFromScene_Obj(_pathFile: Path, _objX: bpy.types.Object):
    with _TempContextForObject(_objX):
        bpy.ops.export_scene.obj(
            filepath=_pathFile.as_posix(),
            check_existing=False,
            use_selection=True,
            use_animation=False,
            use_mesh_modifiers=True,
            use_edges=True,
            use_smooth_groups=False,
            use_smooth_groups_bitflags=False,
            use_normals=True,
            use_uvs=True,
            use_materials=True,
            use_triangles=False,
            use_nurbs=False,
            use_vertex_groups=False,
            use_blen_objects=True,
            group_by_material=False,
            group_by_object=False,
            keep_vertex_order=False,
            global_scale=1,
            path_mode="AUTO",
            axis_forward="-Z",
            axis_up="Y",
        )
    # endwith


# enddef


######################################################
def SmartUvUnwrap(_objX: bpy.types.Object, *, _fAngleLimit_deg: float = 66.0, _fIslandMargin: float = 0.0):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = _objX
    _objX.select_set(True)

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action="SELECT")

    fAngleLimit_rad = math.radians(_fAngleLimit_deg)

    # Smart UV unwrap
    bpy.ops.uv.smart_project(angle_limit=fAngleLimit_rad, island_margin=_fIslandMargin)
    bpy.ops.object.mode_set(mode="OBJECT")


# enddef
