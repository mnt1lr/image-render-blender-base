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
import math

from typing import Union, Optional, Tuple
from pathlib import Path
from .mesh.types import CMeshData
from .node import shader as nsh
from .node import align as nalign
from .node.shader import utils as nutils
from .util.node import GetByLabelOrId as GetNodeByLabelOrId

# import sys
# import copy
# import math

import numpy as np

# import random

from . import collection
from . import viewlayer
from . import ops_object as ops
from . import ops_image


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

    if hasattr(meshX, "use_auto_smooth"):
        meshX.use_auto_smooth = True
    # endif

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
def _GetChildMeshObjectNames(_objParent: bpy.types.Object, *, _bRecursive: bool = True) -> list[str]:
    lChildren: list[str] = []
    for objChild in _objParent.children:
        if objChild.type == "MESH":
            lChildren.append(objChild.name)
        elif objChild.type == "EMPTY" and _bRecursive is True:
            lChildren.extend(_GetChildMeshObjectNames(objChild))
        # endif
    # endfor

    return lChildren


# enddef


################################################################################
def JoinHierarchyToObject(_objIn: bpy.types.Object) -> str:
    if _objIn.type == "EMPTY":
        lObjects = _GetChildMeshObjectNames(_objIn, _bRecursive=True)
        if len(lObjects) == 0:
            return None
        # endif

        bpy.ops.object.select_all(action="DESELECT")

        for sObjName in lObjects:
            bpy.data.objects[sObjName].select_set(True)
        # endfor
        sNewObj: str = lObjects[0]
        sObjInName: str = _objIn.name

        bpy.context.view_layer.objects.active = bpy.data.objects[sNewObj]
        bpy.ops.object.join()
        bpy.ops.object.select_all(action="DESELECT")
        objNew: bpy.types.Object = bpy.data.objects[sNewObj]
        objNew.parent = _objIn.parent
        RemoveObjectHierarchy(_objIn)
        objNew.name = sObjInName

        return objNew.name

    elif _objIn.type == "MESH":
        return _objIn.name
    # endif

    return None


# enddef


################################################################################
def JoinObjectList(_lObjNames: list[str], _sNewName: str) -> str:
    lObjects: list[str] = []

    for sObjName in _lObjNames:
        objX: bpy.types.Object = bpy.data.objects.get(sObjName)
        if objX is None:
            continue
        # endif

        if objX.type == "EMPTY":
            lChildObj = _GetChildMeshObjectNames(objX, _bRecursive=True)
            lObjects.extend(lChildObj)
        elif objX.type == "MESH":
            lObjects.append(sObjName)
        # endif
    # endfor

    bpy.ops.object.select_all(action="DESELECT")

    for sObjName in lObjects:
        bpy.data.objects[sObjName].select_set(True)
    # endfor
    sNewObj: str = lObjects[0]
    objMain = bpy.data.objects[sNewObj]
    objParent: bpy.types.Object = objMain.parent

    bpy.context.view_layer.objects.active = objMain
    bpy.ops.object.join()
    bpy.ops.object.select_all(action="DESELECT")
    objNew: bpy.types.Object = bpy.data.objects[sNewObj]
    objNew.parent = objParent
    objNew.name = _sNewName

    return objNew.name


# enddef


################################################################################
def ImportObjectAny(
    *,
    _pathFile: Path,
    _sNewName: str = None,
    _fScaleFactor: float = None,
    _bDoSetOrigin: bool = False,
    _sSetOriginType: str = None,
    _sSetOriginCenter: str = None,
    _lLocation: list[float] = None,
    _lRotationEuler_deg: list[float] = None,
    _bDoJoinObjects: bool = False,
) -> list[str]:
    lObjIn: list[str]
    if _pathFile.suffix == ".obj":
        lObjIn = ops.ImportToScene_Obj(_pathFile)
    elif _pathFile.suffix == ".fbx":
        lObjIn = ops.ImportToScene_Fbx(_pathFile)
    elif _pathFile.suffix in [".glb", ".gltf"]:
        lObjIn = ops.ImportToScene_Glb(_pathFile)
    else:
        lSupportedTypes: list[str] = [".obj", ".fbx", ".glb", ".gltf"]
        sSupTypes: str = ", ".join(lSupportedTypes)
        raise RuntimeError(f"File type '{_pathFile.suffix}' not supported. Supported types are: [{sSupTypes}]")
    # endif

    # Only keep those objects in the list of imported objects, that are not parented
    # to any of the other imported objects
    lObjIn = [
        sName
        for sName in lObjIn
        if bpy.data.objects[sName].parent is None or bpy.data.objects[sName].parent.name not in lObjIn
    ]

    lCreationNames: list[str] = []
    for sObjIn in lObjIn:
        objIn = bpy.data.objects[sObjIn]
        if objIn.type == "EMPTY":
            if _bDoJoinObjects is True:
                sNewObj = JoinHierarchyToObject(objIn)
            else:
                lChildren: list[str] = GetObjectChildrenNames(objIn, bRecursive=True)
                for sChild in lChildren:
                    objChild: bpy.types.Object = bpy.data.objects[sChild]
                    if objChild.type == "MESH":
                        lCreationNames.append(sChild)
                        objChild.parent = objIn.parent
                    # endif
                # endfor
                RemoveObjectHierarchy(objIn)
                sNewObj = None
            # endif
        elif objIn.type == "MESH":
            sNewObj = objIn.name
        else:
            sNewObj = None
        # endif
        if sNewObj is not None:
            lCreationNames.append(sNewObj)
        # endif
    # endif

    if len(lCreationNames) > 1 and _bDoJoinObjects is True:
        if _sNewName is not None:
            sNewName = _sNewName
        else:
            sNewName = lCreationNames[0]
        # endif
        sNewObj = JoinObjectList(lCreationNames, sNewName)
        lObjIn = [sNewObj]
    else:
        lObjIn = lCreationNames
    # endif

    if isinstance(_fScaleFactor, float):
        for sObjIn in lObjIn:
            objIn = bpy.data.objects[sObjIn]
            objIn.scale *= mathutils.Vector((_fScaleFactor, _fScaleFactor, _fScaleFactor))
        # endfor
    # endif

    if _bDoSetOrigin is True:
        for sObjIn in lObjIn:
            objIn = bpy.data.objects[sObjIn]
            ops.SetOriginByType(objIn, _sOriginType=_sSetOriginType, _sCenter=_sSetOriginCenter)
        # endfor
    # endif

    if isinstance(_lLocation, list):
        if len(_lLocation) != 3:
            raise RuntimeError(f"Invalid location for object: {_lLocation}")
        # endif
        for sObjIn in lObjIn:
            objIn = bpy.data.objects[sObjIn]
            objIn.location = mathutils.Vector(_lLocation)
        # endfor
    # endif

    if isinstance(_lRotationEuler_deg, list):
        if len(_lRotationEuler_deg) != 3:
            raise RuntimeError(f"Invalid rotation for object: {_lRotationEuler_deg}")
        # endif
        lRot_rad = [math.radians(x) for x in _lRotationEuler_deg]

        for sObjIn in lObjIn:
            objIn = bpy.data.objects[sObjIn]
            objIn.rotation_euler = mathutils.Vector(lRot_rad)
        # endfor
    # endif

    if isinstance(_fScaleFactor, float) or _bDoSetOrigin is True:
        for sObjIn in lObjIn:
            objIn = bpy.data.objects[sObjIn]
            ops.ApplyTransforms(objIn)
        # endfor
    # enddef

    # print(lObjIn)
    if isinstance(_sNewName, str):
        lNewObjIn: list[str] = []
        if len(lObjIn) > 1:
            for iIdx, sObjIn in enumerate(lObjIn):
                objIn = bpy.data.objects[sObjIn]
                objIn.name = f"{_sNewName}-{iIdx}"
                lNewObjIn.append(objIn.name)
            # endfor
        elif len(lObjIn) == 1:
            objIn = bpy.data.objects[lObjIn[0]]
            objIn.name = _sNewName
            lNewObjIn.append(objIn.name)
        # endif
        lObjIn = lNewObjIn
    # endif
    # print(lObjIn)

    return lObjIn


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


################################################################################
def VoxelRemesh_BakeTexture(
    *,
    _objIn: bpy.types.Object,
    _fRemeshVoxelSize: float,
    _bRemeshSmoothShade: bool = True,
    _bDoSmoothSurface: bool = True,
    _iSmoothIterations: int = 3,
    _fSmoothFactor: float = 0.5,
    _iMultiResIterCnt: int = 2,
    _sLowPolyObjName: Optional[str] = None,
    _tBakedTexRes: Tuple[int, int] = (2048, 2048),
    _fBakedTexCageExtrusion: float = 0.1,
    _pathTex: Optional[Path] = None,
):
    if _objIn is None or not isinstance(_objIn, bpy.types.Object) or _objIn.type != "MESH":
        raise RuntimeError("Given object argument is not a Blender mesh object")
    # endif

    tNodeSpace = (70, 25)
    tNodeSpaceSmall = (30, 15)

    mshIn: bpy.types.Mesh = _objIn.data
    if hasattr(mshIn, "use_auto_smooth"):
        mshIn.use_auto_smooth = False
    # endif
    
    objLp: bpy.types.Object = ops.Duplicate(_objIn)
    if _sLowPolyObjName is not None and isinstance(_sLowPolyObjName, str):
        objLp.name = _sLowPolyObjName
    # endif
    mshLp: bpy.types.Mesh = objLp.data
    if hasattr(mshLp, "use_auto_smooth"):
        mshLp.use_auto_smooth = False
    # endif

    # ########################################################################################
    # Remesh & Smooth to create low poly object

    modRemesh = ops.AddModifier_Remesh(objLp)
    modRemesh.voxel_size = _fRemeshVoxelSize
    modRemesh.use_smooth_shade = _bRemeshSmoothShade
    ops.ApplyModifier(objLp, modRemesh)

    if _bDoSmoothSurface is True:
        modSmooth: bpy.types.SmoothModifier = ops.AddModifier(objLp, "SMOOTH")
        modSmooth.iterations = _iSmoothIterations
        modSmooth.factor = _fSmoothFactor
        ops.ApplyModifier(objLp, modSmooth)
    # endif

    # add multires modifier to active object
    modMultiRes = ops.AddModifier_MultiRes(objLp)

    # add shrinkwrap modifier
    modShrinkWrap = ops.AddModifier_Shrinkwrap(objLp)
    modShrinkWrap.wrap_method = "PROJECT"
    modShrinkWrap.use_negative_direction = True
    modShrinkWrap.use_positive_direction = True
    modShrinkWrap.target = _objIn

    # Apply multires subdivision for low poly object
    ops.DoMultiResSubdivide(objLp, modMultiRes, _iMultiResIterCnt, _sMode="CATMULL_CLARK")

    # Set viewport multires level to 0
    # INFO: The normal baking creates a normal map that is the difference between the viewport level
    #       and the render level.
    modMultiRes.levels = 0

    ops.ApplyModifier(objLp, modShrinkWrap)

    # ########################################################################################
    # Create new material for objLp
    # DO NOT connect texture nodes to Prinicipled Shader yet! Otherwise baking throws recursion warning.
    matLp = ops.SetNewMaterial(objLp, _sMaterialName=f"{objLp.name}_baked")
    sMatName = matLp.name

    # Create images
    iResX, iResY = _tBakedTexRes
    imgDiffuse = bpy.data.images.new(f"{sMatName}_diffuse", iResX, iResY, alpha=True, float_buffer=False)
    imgNormal = bpy.data.images.new(f"{sMatName}_normal", iResX, iResY, alpha=False, float_buffer=True)

    if _pathTex is not None:
        imgDiffuse.filepath_raw = (_pathTex / f"{imgDiffuse.name}.png").as_posix()
        imgNormal.filepath_raw = (_pathTex / f"{imgNormal.name}.png").as_posix()
    # endif

    imgDiffuse.use_fake_user = True
    imgNormal.use_fake_user = True

    # Create texture nodes
    ntMain = matLp.node_tree
    nodShader = ntMain.nodes.get("Principled BSDF")

    sklTexDiff = nsh.tex.Image(
        ntMain,
        "Diffuse",
        None,
        imgDiffuse.name,
        eExtension=nsh.tex.EExtension.EXTEND,
        eProjection=nsh.tex.EProjection.FLAT,
        eInterpolation=nsh.tex.EInterpolation.LINEAR,
        eColorSpace=nsh.tex.EColorSpace.SRGB,
        eAlphaMode=nsh.tex.EAlphaMode.STRAIGHT,
    )
    nalign.Relative(nodShader, (-1, 0), sklTexDiff, (1, 0), tNodeSpace)

    sklTexNorm = nsh.tex.Image(
        ntMain,
        "Normal",
        None,
        imgNormal.name,
        eExtension=nsh.tex.EExtension.EXTEND,
        eProjection=nsh.tex.EProjection.FLAT,
        eInterpolation=nsh.tex.EInterpolation.LINEAR,
        eColorSpace=nsh.tex.EColorSpace.NON_COLOR,
        eAlphaMode=nsh.tex.EAlphaMode.NONE,
    )
    nalign.Relative(sklTexDiff, (0, 2), sklTexNorm, (0, 0), tNodeSpace)

    sklNormalMap = nsh.vector.NormalMap(ntMain, "Normal Map", sklTexNorm["Color"])
    nalign.Relative(sklTexNorm, (1, 0), sklNormalMap, (0, 0), tNodeSpaceSmall)

    # ########################################################################################
    # UV Unwrap
    ops.SmartUvUnwrap(objLp, _fAngleLimit_deg=66.0, _fIslandMargin=0.01)

    # #######################################################################
    # Texture baking
    # https://docs.blender.org/api/current/bpy.ops.object.html

    # Make original and lp shade smooth
    with ops._TempContextForObject(objLp):
        bpy.ops.object.shade_smooth()
    # endwith
    with ops._TempContextForObject(_objIn):
        bpy.ops.object.shade_smooth()
    # endwith

    xScene = bpy.context.scene
    xRender = xScene.render
    xCycles = xScene.cycles

    # Store Render Values
    dicRender = {
        "engine": xRender.engine,
        "use_bake_multires": xRender.use_bake_multires,
        "bake/cage_extrusion": xRender.bake.cage_extrusion,
        "bake_type": xRender.bake_type,
    }

    # Store Cycles Values
    dicCycles = {
        "device": xCycles.device,
        "preview_samples": xCycles.preview_samples,
        "samples": xCycles.samples,
        "use_denoising": xCycles.use_denoising,
        "bake_type": xCycles.bake_type,
    }

    # Set general baking values
    xRender.engine = "CYCLES"
    xCycles.device = "GPU"
    xCycles.preview_samples = 16
    xCycles.samples = 16
    xCycles.use_denoising = True

    matLp = mshLp.materials[0]
    nodTexNorm: bpy.types.Node = GetNodeByLabelOrId(matLp.node_tree, "Normal")
    nodTexDiff: bpy.types.Node = GetNodeByLabelOrId(matLp.node_tree, "Diffuse")

    # #################################################
    # Bake DIFFUSE
    # select both objOrig, objLP, but make objLp active
    bpy.ops.object.select_all(action="DESELECT")
    _objIn.hide_render = False
    _objIn.hide_set(False)
    _objIn.select_set(True)
    objLp.select_set(True)
    objLp.hide_render = False
    bpy.context.view_layer.objects.active = objLp

    nodTexDiff.select = True
    matLp.node_tree.nodes.active = nodTexDiff
    nodTexNorm.select = False

    xRender.use_bake_multires = False
    xRender.bake.cage_extrusion = _fBakedTexCageExtrusion
    xCycles.bake_type = "DIFFUSE"

    bpy.ops.object.bake(type="DIFFUSE", use_selected_to_active=True, pass_filter={"COLOR"})

    # ensure that low poly object is active and selected
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = objLp
    objLp.select_set(True)

    _objIn.hide_render = True
    _objIn.hide_set(True)

    # #################################################
    # Bake NORMALS
    # Settings for multires bake
    xRender.use_bake_multires = True
    xRender.bake_type = "NORMALS"

    for nodX in matLp.node_tree.nodes:
        nodX.select = False
    # endfor
    matLp.node_tree.nodes.active = nodTexNorm
    nodTexNorm.select = True

    bpy.ops.object.bake(type="NORMAL")

    # #################################################
    # Restore render and Cycles values
    xRender.engine = dicRender["engine"]
    xRender.use_bake_multires = dicRender["use_bake_multires"]
    xRender.bake.cage_extrusion = dicRender["bake/cage_extrusion"]
    xRender.bake_type = dicRender["bake_type"]

    xCycles.device = dicCycles["device"]
    xCycles.preview_samples = dicCycles["preview_samples"]
    xCycles.samples = dicCycles["samples"]
    xCycles.use_denoising = dicCycles["use_denoising"]
    xCycles.bake_type = dicCycles["bake_type"]

    # #######################################################################
    # Save texture images to disk or store in Blender file

    if _pathTex is not None:
        # Store texture images if a path is given
        imgDiffuse.save()
        imgNormal.save()

    else:
        # Pack textures in Blender file
        ops_image.Pack(imgDiffuse)
        ops_image.Pack(imgNormal)
    # endif

    # #######################################################################
    # Connect shader nodes in Material shader
    ntMain = matLp.node_tree

    nodNormMap: bpy.types.Node = GetNodeByLabelOrId(matLp.node_tree, "Normal Map")
    nodTexDiff: bpy.types.Node = GetNodeByLabelOrId(matLp.node_tree, "Diffuse")
    nodShader: bpy.types.ShaderNodeBsdfPrincipled = GetNodeByLabelOrId(matLp.node_tree, "Principled BSDF")

    nutils._ConnectWithSocket(ntMain, nodShader.inputs["Normal"], nodNormMap.outputs["Normal"])
    nutils._ConnectWithSocket(ntMain, nodShader.inputs["Base Color"], nodTexDiff.outputs["Color"])

    # #######################################################################
    # Clean-up
    objLp.modifiers.clear()

    return objLp


# enddef
