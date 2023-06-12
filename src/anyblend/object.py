#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \blend\object.py
# Created Date: Thursday, April 29th 2021, 2:22:08 pm
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
import bmesh

import mathutils
from typing import Union, Optional
from pathlib import Path
from .mesh.types import CMeshData

# import sys
# import copy
# import math

import numpy as np

# import random

from . import collection
from . import viewlayer
from . import ops_object as ops


################################################################################
def CreateObject(_xContext, _sName, bActivate=False, xCollection=None):

    if xCollection is None:
        xCln = collection.GetActiveCollection(_xContext)
    else:
        xCln = xCollection
    # endif

    meshA = bpy.data.meshes.new(_sName)
    objA = bpy.data.objects.new(_sName, meshA)
    xCln.objects.link(objA)

    if bActivate:
        _xContext.view_layer.objects.active = objA
        objA.select_set(True)
    # endif

    return objA


# enddef


################################################################################
def CreateMeshObject(
    _sName: str,
    *,
    _bActivate: bool = False,
    _xCollection: Optional[bpy.types.Collection] = None,
    _xContext: Optional[bpy.types.Context] = None,
) -> bpy.types.Object:

    xCtx: bpy.types.Context = None
    if _xContext is None:
        xCtx = bpy.context
    else:
        xCtx = _xContext
    # endif

    xCln: bpy.types.Collection = None
    if _xCollection is None:
        xCln = collection.GetActiveCollection(xCtx)
    else:
        xCln = _xCollection
    # endif

    meshA: bpy.types.Mesh = bpy.data.meshes.new(_sName)
    objA: bpy.types.Object = bpy.data.objects.new(_sName, meshA)
    xCln.objects.link(objA)

    if _bActivate:
        xCtx.view_layer.objects.active = objA
        objA.select_set(True)
    # endif

    return objA


# enddef


# ########################################################################################################
# Create a mesh object from a CMeshData instance
def CreateObjectFromMeshData(
    _sName: str,
    _xMeshData: CMeshData,
    *,
    _bSmoothNormals: bool = True,
    _bActivate: bool = False,
    _xCollection: Optional[bpy.types.Collection] = None,
    _xContext: bpy.types.Context = None,
) -> bpy.types.Object:

    objX = CreateMeshObject(_sName, _bActivate=_bActivate, _xCollection=_xCollection, _xContext=_xContext)
    meshX: bpy.types.Mesh = objX.data

    # Ensure lens object is initially at origin, so that mesh vertices
    # can be places relative to origin.
    objX.location = (0, 0, 0)

    meshX.from_pydata(_xMeshData.lVex, _xMeshData.lEdges, _xMeshData.lFaces)
    meshX.update(calc_edges=True)
    meshX.use_auto_smooth = True

    bm: bmesh.types.BMesh = bmesh.new()
    bm.from_mesh(meshX)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(meshX)
    meshX.update()
    bm.free()

    xPoly: bpy.types.MeshPolygon
    for xPoly in meshX.polygons:
        xPoly.use_smooth = _bSmoothNormals
    # endfor

    return objX


# enddef


################################################################################
def CreateEmpty(_xContext, _sName, bActivate=False, xCollection=None):

    if xCollection is None:
        xCln = collection.GetActiveCollection(_xContext)
    else:
        xCln = xCollection
    # endif

    objA = bpy.data.objects.new(_sName, None)
    xCln.objects.link(objA)

    if bActivate:
        _xContext.view_layer.objects.active = objA
        objA.select_set(True)
    # endif

    return objA


# enddef


################################################################################
def CreateText(
    _sText: str,
    *,
    _sName: str = "Text",
    _sAlignX: str = "LEFT",
    _sAlignY: str = "BOTTOM",
    _fSize: float = 1.0,
    _xDir: Union[list[float], mathutils.Vector, None] = None,
    _xContext: bpy.types.Context = None,
    _xCollection: bpy.types.Collection = None,
    _bActivate: bool = False,
):

    xCtx: bpy.types.Context = bpy.context
    if _xContext is not None:
        xCtx = _xContext
    # endif

    if _xCollection is None:
        xCln = collection.GetActiveCollection(xCtx)
    else:
        xCln = _xCollection
    # endif

    vDir: mathutils.Vector = None
    if _xDir is None:
        vDir = None
    else:
        try:
            vDir = mathutils.Vector(_xDir)
            vDir.normalize()
        except Exception:
            raise RuntimeError(f"Invalid direction vector for text object '{_sText}'")
        # endtry
    # endif

    crvText: bpy.types.TextCurve = bpy.data.curves.new(type="FONT", name=_sName)
    crvText.body = _sText
    crvText.align_x = _sAlignX
    crvText.align_y = _sAlignY
    crvText.size = _fSize

    objText: bpy.types.Object = bpy.data.objects.new(name=_sName, object_data=crvText)

    xCln.objects.link(objText)

    if _bActivate:
        xCtx.view_layer.objects.active = objText
        objText.select_set(True)
    # endif

    if vDir is not None:
        objText.rotation_euler = vDir.to_track_quat("X", "Z").to_euler()
    # endif

    viewlayer.Update()

    return objText


# enddef


# #####################################################
def _DoCopyObject(_objTop, *, _clnX, _bLinked=False, _bHierarchy=False):

    objX = _objTop.copy()
    if _bLinked is False and _objTop.data is not None:
        objX.data = _objTop.data.copy()
    # endif
    _clnX.objects.link(objX)

    if _bHierarchy is True:
        for objChild in _objTop.children:
            objY = _DoCopyObject(objChild, _clnX=_clnX, _bLinked=_bLinked, _bHierarchy=_bHierarchy)
            ParentObject(objX, objY, bKeepTransform=True)
        # endfor
    # endif

    return objX


# enddef

# #####################################################
def CopyObject(_objTop, *, _bLinked=False, _bHierarchy=False, _clnTarget=None):

    if _clnTarget is None:
        clnX = collection.FindCollectionOfObject(bpy.context, _objTop)
    else:
        clnX = _clnTarget
    # endif

    objX = _DoCopyObject(_objTop, _clnX=clnX, _bLinked=_bLinked, _bHierarchy=_bHierarchy)

    return objX


# enddef


# #####################################################
def CopyCollection(_clnX, *, _bLinked=False, _bObjectHierarchy=True, _clnTarget=None, _xContext=None):

    if _xContext is None:
        xCtx = bpy.context
    else:
        xCtx = _xContext
    # endif

    if _clnTarget is None:
        clnParent = collection.GetParentCollection(_clnX)
    else:
        clnParent = _clnTarget
    # endif

    clnY = collection.CreateCollection(xCtx, _clnX.name, bActivate=False, clnParent=clnParent)
    for objX in _clnX.objects:
        if objX.parent is None or (objX.parent is not None and objX.parent.name not in _clnX.objects):
            CopyObject(objX, _bLinked=_bLinked, _bHierarchy=_bObjectHierarchy, _clnTarget=clnY)
        # endif
    # endfor

    for clnChild in _clnX.children:
        CopyCollection(
            clnChild, _bLinked=_bLinked, _bObjectHierarchy=_bObjectHierarchy, _clnTarget=clnY, _xContext=xCtx
        )
    # endfor

    return clnY


# enddef


####################################################################
def CreateEvaluatedMeshObject(_xContext, _objMesh, _sNewName):

    # https://docs.blender.org/api/current/bpy.types.Depsgraph.html
    xDG = _xContext.evaluated_depsgraph_get()

    objEvalMesh = _objMesh.evaluated_get(xDG)
    meshNew = bpy.data.meshes.new_from_object(objEvalMesh)

    # objX = bpy.data.objects.new(_sNewName, meshNew)
    # Copy the original object, replace the mesh and remove
    # all modifiers that are not particle systems.
    objX = _objMesh.copy()
    objX.name = _sNewName
    objX.data = meshNew

    lModNames = [x.name for x in objX.modifiers if x.type != "PARTICLE_SYSTEM"]

    for sModName in lModNames:
        modX = objX.modifiers.get(sModName)
        objX.modifiers.remove(modX)
    # endfor

    clnX = collection.FindCollectionOfObject(_xContext, _objMesh)
    if clnX is not None:
        clnX.objects.link(objX)
    # endif

    if _objMesh.parent is not None:
        ParentObject(_objMesh.parent, objX, bKeepTransform=False)
    # endif

    objX.location = _objMesh.location.copy()
    objX.rotation_euler = _objMesh.rotation_euler.copy()
    objX.matrix_parent_inverse = _objMesh.matrix_parent_inverse.copy()

    return objX


# enddef


################################################################################
def Hide(_objX, bHide=None, bHideRender=None, bHideInAllViewports=None, bRecursive=True):

    if isinstance(bHide, bool):
        _objX.hide_set(bHide)
    # endif

    if isinstance(bHideRender, bool):
        _objX.hide_render = bHideRender
    # endif

    if isinstance(bHideInAllViewports, bool):
        _objX.hide_viewport = bHideInAllViewports
    # endif

    if bRecursive is True:
        for objY in _objX.children:
            Hide(
                objY,
                bHide=bHide,
                bHideRender=bHideRender,
                bHideInAllViewports=bHideInAllViewports,
            )
        # endfor
    # endif recusive


# enddef

################################################################################
def GetActiveObject(_xContext):
    return _xContext.active_object


# enddef

################################################################################
def ParentObject(_objParent, _objChild, bKeepTransform=True, bKeepRelTransform=False):

    # sys.stderr.write(f"\n>>>>> bKeepTransform: {bKeepTransform}\n")
    # sys.stderr.write(f"\n>>>>> bKeepRelTransform: {bKeepRelTransform}\n")
    # sys.stderr.flush()

    matChild_world = _objChild.matrix_world.copy()
    _objChild.parent = _objParent

    if bKeepTransform is True:
        _objChild.matrix_parent_inverse.identity()
        _objChild.matrix_basis = _objParent.matrix_world.inverted() @ matChild_world

    elif bKeepRelTransform is False:
        _objChild.matrix_parent_inverse.identity()
        _objChild.matrix_basis.identity()
    # endif


# enddef


################################################################################
def ParentObjectList(_objParent, _lobjChild, bKeepTransform=True):
    for objChild in _lobjChild:
        ParentObject(_objParent, objChild, bKeepTransform=bKeepTransform)
    # endfor


# enddef


######################################################
# Get list of names of children of Object
def GetObjectChildrenNames(_objMain, bRecursive=False):

    lNames = []
    for objChild in _objMain.children:
        lNames.append(objChild.name)
        if bRecursive and objChild.children is not None:
            lNames += GetObjectChildrenNames(objChild, bRecursive=True)
        # endif
    # endfor

    return lNames


# enddef


######################################################
# Remove object hierarchy
def RemoveObjectHierarchy(_objMain):
    """Removes the given object and its' hierarchy.

    Args:
        _objMain (blender object): The object to remove together with its' hierarchy.
    """

    lNames = [_objMain.name]
    lNames += GetObjectChildrenNames(_objMain, bRecursive=True)

    # print(lNames)
    for sName in lNames:
        objX = bpy.data.objects.get(sName)
        objX.animation_data_clear()
        bpy.data.objects.remove(objX)
    # endfor


# enddef


################################################################################
def ScaleObject(_objX, _fScale: float, *, _bApply: bool = False):

    if _bApply is True and hasattr(_objX.data, "transform"):
        # print(f"Scaling '{_objX.name}' with factor {_fScale}")

        vLoc, qRot, vScale = _objX.matrix_basis.decompose()
        matT = mathutils.Matrix.Translation(vLoc)
        matR = qRot.to_matrix().to_4x4()
        matS = mathutils.Matrix.Diagonal(vScale * _fScale).to_4x4()
        _objX.data.transform(matS)
        _objX.matrix_basis = matT @ matR

    else:
        _objX.scale = mathutils.Vector((_fScale, _fScale, _fScale))

    # endif


# enddef


######################################################
# Get Mesh Vertices as numpy array
def GetMeshVex(
    _objX: bpy.types.Object, *, sFrame: str = "WORLD", bUseParentFrame: bool = True, bEvaluated: bool = False
) -> np.ndarray:

    if _objX.type != "MESH":
        raise Exception("Object '{0}' is not a mesh object".format(_objX.name))
    # endif

    lAllowedFrames = ["WORLD", "LOCAL", "ID"]
    if sFrame not in lAllowedFrames:
        raise Exception(
            "Frame parameter must be one of {}, but has value '{}'.".format(", ".join(lAllowedFrames), sFrame)
        )
    # endif

    if sFrame == "WORLD":
        mFrame = _objX.matrix_world

    elif sFrame == "LOCAL":
        mFrame = _objX.matrix_local
        if bUseParentFrame is True and _objX.parent is not None:
            mFrame = _objX.parent.matrix_local @ mFrame
        # endif

    else:
        mFrame = None
    # endif

    if mFrame is not None:
        mFrameT = np.array(mFrame.to_3x3()).transpose()
        mTrans = np.array(mFrame.translation)
    # endif

    if bEvaluated is True:
        xDG = bpy.context.evaluated_depsgraph_get()
        objMesh = _objX.evaluated_get(xDG)
        meshX = objMesh.data
    else:
        meshX = _objX.data
    # endif

    iVexCnt = len(meshX.vertices)
    aVex = np.empty(iVexCnt * 3, dtype=np.float64)
    meshX.vertices.foreach_get("co", aVex)

    aVex.shape = (iVexCnt, 3)
    if mFrame is not None:
        aVex = (aVex @ mFrameT) + mTrans
    # endif

    return aVex


# enddef


######################################################
def GetVertexWeights(_objX, _sGrpName):
    """Get the vertex weights for all vertices of the given object,
    using the given vertex group. If a vertex is not part of that
    vertex group, the corresponding weight is set to zero.

    Args:
        _objX (bpy.types.Object): The object.
        _sGrpName (str): The name of the vertex group to use.

    Raises:
        RuntimeError: if the vertex group does not exist for the object.

    Returns:
        list: The list of vertex group weights for every vertex of the object.
    """

    iVexCnt = len(_objX.data.vertices)

    # if no vertex group name is given
    if _sGrpName is None:
        return [1.0] * iVexCnt
    # endif

    lW = [0.0] * iVexCnt
    xGrp = _objX.vertex_groups.get(_sGrpName)
    if xGrp is None:
        raise RuntimeError("Vertex group '{}' does not exist in object '{}'".format(_sGrpName, _objX.name))
    # endif

    for i, xVex in enumerate(_objX.data.vertices):
        for xG in xVex.groups:
            if xG.group == xGrp.index:
                lW[i] = xG.weight
            # endif target group
        # endfor vertex groups
    # endfor vertices

    return lW


# enddef


######################################################
def GetMeshObjectDist(*, objTrg, objX, vDir):

    matT = objTrg.matrix_world.inverted() @ objX.matrix_world
    vDir_loc = (objTrg.matrix_world.inverted().to_3x3() @ vDir).normalized()

    fDistMin = 1e20
    fDistMax = -1e20

    for vexOrig in objX.data.vertices:
        vOrig = matT @ vexOrig.co

        tR = objTrg.ray_cast(vOrig, vDir_loc)
        if tR[0] is True:
            fDist = (vOrig - tR[1]).length
        else:
            tR = objTrg.ray_cast(vOrig, -vDir_loc)
            if tR[0] is True:
                fDist = -(vOrig - tR[1]).length
            else:
                fDist = None
            # endif
        # endif
        if fDist is not None:
            fDistMin = min(fDistMin, fDist)
            fDistMax = max(fDistMax, fDist)
        # endif
    # endfor

    # Transform the delta vector back to world coordinates,
    # in case there is a scaling in the target object
    fDistMin = vDir.dot(objTrg.matrix_world.to_3x3() @ (fDistMin * vDir_loc))
    fDistMax = vDir.dot(objTrg.matrix_world.to_3x3() @ (fDistMax * vDir_loc))

    return (fDistMin, fDistMax)


# enddef


######################################################
def GetMeshObjectHierarchy(_objTop):

    lObjects = []
    if _objTop.type == "MESH":
        lObjects.append(_objTop)
    # endif

    for objX in _objTop.children:
        lObjects.extend(GetMeshObjectHierarchy(objX))
    # endfor

    return lObjects


# enddef

######################################################
def GetObjectDeltaToMesh(*, objTrg, objX, vDir, sMode="ABOVE"):

    lAllowedModes = ["CLOSEST", "ABOVE", "BELOW"]
    if sMode not in lAllowedModes:
        raise RuntimeError("sMode must be one of 'CLOSEST', 'ABOVE' or 'BELOW'")
    # endif

    # print("\n>>> GetObjectDeltaToMesh: Frame {}".format(bpy.context.scene.frame_current))

    # Get the current dependency graph
    xDG = bpy.context.evaluated_depsgraph_get()

    # Get all mesh objects in the object hierarchy
    lObjects = GetMeshObjectHierarchy(objX)

    fDistMin = 1e20
    fDistMax = -1e20

    objTrg_eval = objTrg.evaluated_get(xDG)

    # loop over all objects
    for objY in lObjects:

        objY_eval = objY.evaluated_get(xDG)
        fMin, fMax = GetMeshObjectDist(objTrg=objTrg_eval, objX=objY_eval, vDir=vDir)

        fDistMin = min(fDistMin, fMin)
        fDistMax = max(fDistMax, fMax)
    # endfor

    # print(fDistMin)
    # print(fDistMax)

    if sMode == "CLOSEST":
        if fDistMin < 0.0 and fDistMax > 0.0:
            if abs(fDistMin) < fDistMax:
                vDelta = fDistMin * vDir
            else:
                vDelta = fDistMax * vDir
            # endif
        elif fDistMax < 0.0:
            vDelta = fDistMax * vDir
        elif fDistMin > 0.0:
            vDelta = fDistMin * vDir
        # endif
    elif sMode == "ABOVE":
        vDelta = fDistMin * vDir
    elif sMode == "BELOW":
        vDelta = fDistMax * vDir
    # endif

    return vDelta


# enddef


################################################################################
def ImportObjectObj(
    *,
    _pathFile: Path,
    _sNewName: str = None,
    _fScaleFactor: float = None,
    _bDoSetOrigin: bool = False,
    _sSetOriginType: str = None,
    _sSetOriginCenter: str = None,
    _lLocation: list[float] = None,
    _lRotationEuler: list[float] = None,
):

    objIn: bpy.types.Object = ops.ImportToScene_Obj(_pathFile)

    if isinstance(_fScaleFactor, float):
        objIn.scale *= mathutils.Vector((_fScaleFactor, _fScaleFactor, _fScaleFactor))
    # endif

    if _bDoSetOrigin is True:
        ops.SetOriginByType(objIn, _sOriginType=_sSetOriginType, _sCenter=_sSetOriginCenter)
    # endif

    if isinstance(_lLocation, list):
        if len(_lLocation) != 3:
            raise RuntimeError(f"Invalid location for object: {_lLocation}")
        # endif
        objIn.location = mathutils.Vector(_lLocation)
    # endif

    if isinstance(_lRotationEuler, list):
        if len(_lRotationEuler) != 3:
            raise RuntimeError(f"Invalid rotation for object: {_lRotationEuler}")
        # endif
        objIn.rotation_euler = mathutils.Vector(_lRotationEuler)
    # endif

    if isinstance(_fScaleFactor, float) or _bDoSetOrigin is True:
        ops.ApplyTransforms(objIn)
    # enddef

    if isinstance(_sNewName, str):
        objIn.name = _sNewName
    # endif

    return objIn


# enddef

################################################################################
def SmoothObjectSurface_VoxelRemesh(_objIn: bpy.types.Object, _fVoxelSize: float):

    objInCopy = ops.Duplicate(_objIn)

    modRemesh = ops.AddModifier_Remesh(objInCopy)
    modRemesh.mode = "VOXEL"
    modRemesh.voxel_size = _fVoxelSize

    modShrink = ops.AddModifier_Shrinkwrap(_objIn)
    modShrink.target = objInCopy
    ops.ApplyModifier(_objIn, modShrink)

    bpy.data.objects.remove(objInCopy)


# enddef
