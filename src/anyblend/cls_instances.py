#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_instances.py
# Created Date: Wednesday, November 2nd 2022, 3:22:44 pm
# Created by: Christian Perwass (CR/AEC5)
# <LICENSE id="GPL-3.0">
#
#   Image-Render standard Blender actions module
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
import math
import random

from typing import Optional, Union, Any, Callable
from anyblend import collection, object
from .cls_boundbox import CBoundingBox
from . import viewlayer


# ################################################################################################
class _CInstance:
    def __init__(self, *, _sName):
        self._sName = _sName
        self._xBoundBox = None

    # enddef

    @property
    def sName(self):
        return self._sName

    # enddef

    @property
    def xBoundBox(self) -> CBoundingBox:
        return self._xBoundBox

    # enddef

    @property
    def vOrigin(self) -> mathutils.Vector:
        raise RuntimeError("Cannot obtain vOrigin from abstract base class")

    # enddef

    def Copy(self, *, _bLinked: bool = False, _clnTarget=None) -> "_CInstance":
        raise RuntimeError("Cannot copy abstract instance base class")

    # enddef

    def Hide(self, _bHide: bool = True):
        raise RuntimeError("Cannot call function 'Hide()' in abstract base class")

    # enddef

    def MoveLocation(self, _xDelta: Union[mathutils.Vector, list, tuple]):
        raise RuntimeError("Cannot call function 'Move()' in abstract base class")

    # enddef

    def RotateEuler(
        self,
        *,
        _lEulerAngles: list[float] = None,
        _bAnglesInDeg: bool = True,
        _lOriginOffset: list[float] = [0.0, 0.0, 0.0],
    ) -> mathutils.Matrix:
        raise RuntimeError("Cannot call function 'RotateEuler()' in abstract base class")

    # enddef

    def GetParentCollection(self) -> bpy.types.Collection:
        raise RuntimeError("Cannot call function 'GetParentCollection()' in abstract base class")

    # enddef

    def ParentTo(self, _sObject: str, _bKeepTransform: bool = True, _bKeepRelTransform: bool = False):
        raise RuntimeError("Cannot call function 'ParentTo()' in abstract base class")

    # enddef


# endclass


# ################################################################################################
class CObjectInstance(_CInstance):
    def __init__(self, *, _sName: str = None, _objX=None):
        if _sName is None:
            if _objX is None:
                raise RuntimeError("An object name or an object have to be given for initialization")
            # endif
            sName = _objX.name
        else:
            sName = _sName
        # endif

        super().__init__(_sName=sName)
        self.EvalBoundingBox()

    # enddef

    @property
    def xObject(self):
        objSrc = bpy.data.objects.get(self.sName)
        if objSrc is None:
            raise RuntimeError(f"Object '{self.sName}' not available")
        # endif
        return objSrc

    # enddef

    @property
    def vOrigin(self) -> mathutils.Vector:
        return self.xObject.matrix_world.to_translation().to_3d()

    # enddef

    # #################################################################################################
    def Copy(self, *, _bLinked: bool = False, _clnTarget=None):
        objTrg = object.CopyObject(self.xObject, _bLinked=_bLinked, _bHierarchy=True, _clnTarget=_clnTarget)

        return CObjectInstance(_objX=objTrg)

    # enddef

    # #################################################################################################
    def EvalBoundingBox(self):
        self._xBoundBox = CBoundingBox(_objX=self.xObject, _bLocal=False)

    # enddef

    # #################################################################################################
    def Hide(self, _bHide: bool = True):
        object.Hide(self.xObject, _bHide, bHideRender=_bHide)

    # enddef

    # #################################################################################################
    def MoveLocation(self, _xDelta: Union[mathutils.Vector, list, tuple]):
        vDelta = mathutils.Vector(_xDelta)
        matT = mathutils.Matrix.Translation(vDelta)
        self.xObject.matrix_world = matT @ self.xObject.matrix_world
        self.xBoundBox.Move(vDelta)

        # Need to update the viewlayer, since the world matrix may
        # only have been changed at a top hierarchy object and all
        # the children still need their world matrices updated.
        viewlayer.Update()

    # enddef

    # #################################################################################################
    def RotateEuler(
        self,
        *,
        _lEulerAngles: list[float] = None,
        _bAnglesInDeg: bool = True,
        _lOriginOffset: list[float] = [0.0, 0.0, 0.0],
    ) -> mathutils.Matrix:
        matTrans = self.xBoundBox.GetRotateEulerMatrix(
            _lEulerAngles=_lEulerAngles, _bAnglesInDeg=_bAnglesInDeg, _lOriginOffset=_lOriginOffset
        )

        objX = self.xObject
        objX.matrix_world = matTrans @ objX.matrix_world

        # Need to update the viewlayer, since the world matrix may
        # only have been changed at a top hierarchy object and all
        # the children still need their world matrices updated.
        viewlayer.Update()

        # Re-evaluate bounding box to ensure z-axis is up.
        self.EvalBoundingBox()

        return matTrans

    # enddef

    # #################################################################################################
    def GetParentCollection(self) -> bpy.types.Collection:
        return collection.FindCollectionOfObject(bpy.context, self.xObject)

    # enddef

    # #################################################################################################
    def ParentTo(self, _sParentObject: str, _bKeepTransform: bool = True, _bKeepRelTransform: bool = False):
        objParent: bpy.types.Object = bpy.data.objects.get(_sParentObject)
        if objParent is None:
            raise RuntimeError(f"Parent object '{_sParentObject}' not found")
        # endif

        object.ParentObject(
            objParent, self.xObject, bKeepTransform=_bKeepTransform, bKeepRelTransform=_bKeepRelTransform
        )

        # Need to update the viewlayer, since the world matrix may
        # only have been changed at a top hierarchy object and all
        # the children still need their world matrices updated.
        viewlayer.Update()

    # enddef


# endclass


# ################################################################################################
class CCollectionInstance(_CInstance):
    def __init__(
        self,
        *,
        _clnX=None,
        _sName: str = None,
        _lObjectTypes: Optional[list[str]] = None,
    ):
        if _sName is None:
            if _clnX is None:
                raise RuntimeError("A collection name or a collection have to be given for initialization")
            # endif
            sName = _clnX.name
        else:
            sName = _sName
            _clnX = bpy.data.collections.get(sName)
            if _clnX is None:
                raise RuntimeError(f"Collection '{sName}' not found")
            # endif
        # endif
        super().__init__(_sName=sName)

        self._lObjectTypes: list[str] = _lObjectTypes
        self._lObjects: list[str] = collection.GetCollectionObjects(
            _clnX, _bChildren=False, _bRecursive=False, _lObjectTypes=_lObjectTypes
        )

        self.EvalBoundingBox()

    # enddef

    @property
    def xCollection(self):
        clnSrc = bpy.data.collections.get(self.sName)
        if clnSrc is None:
            raise RuntimeError(f"Collection '{self.sName}' not available")
        # endif
        return clnSrc

    # enddef

    @property
    def vOrigin(self) -> mathutils.Vector:
        objOrig = None
        # Try to find first empty in list of objects
        for sObjName in self._lObjects:
            objX = bpy.data.objects.get(sObjName)
            if objX.type == "EMPTY":
                objOrig = objX
                break
            # endif
        # endfor

        # If not empty was found, use the first object in the list
        if objOrig is None:
            objOrig = bpy.data.objects.get(self._lObjects[0])
        # endif

        return objOrig.matrix_world.to_translation().to_3d()

    # enddef

    # #################################################################################################
    def Copy(self, *, _bLinked: bool = False, _clnTarget=None):
        clnTrg = object.CopyCollection(
            self.xCollection, _bLinked=_bLinked, _bObjectHierarchy=True, _clnTarget=_clnTarget, _xContext=bpy.context
        )

        return CCollectionInstance(_clnX=clnTrg, _lObjectTypes=self._lObjectTypes)

    # enddef

    # #################################################################################################
    def EvalBoundingBox(self):
        lObjectNames = collection.GetCollectionObjects(
            self.xCollection, _bChildren=True, _bRecursive=True, _lObjectTypes=self._lObjectTypes
        )

        lObjects = []
        for sObjName in lObjectNames:
            objX = bpy.data.objects.get(sObjName)
            if objX is None:
                raise RuntimeError(f"Object '{sObjName}' is not available")
            # endif
            lObjects.append(objX)
        # endfor

        self._xBoundBox = CBoundingBox(_lObjects=lObjects, _bLocal=False)

    # enddef

    # #################################################################################################
    def Hide(self, _bHide: bool = True):
        collection.ExcludeCollection(bpy.context, self.sName, _bHide)

    # enddef

    # #################################################################################################
    def MoveLocation(self, _xDelta: Union[mathutils.Vector, list, tuple]):
        vDelta = mathutils.Vector(_xDelta)
        matT = mathutils.Matrix.Translation(vDelta)

        for sObject in self._lObjects:
            objX = bpy.data.objects.get(sObject)
            if objX is None:
                raise RuntimeError(f"Object '{sObject}' not available")
            # endif

            # xObjBox = CBoundingBox(_objX=objX)
            objX.matrix_world = matT @ objX.matrix_world
        # endfor

        # Need to update the viewlayer, since the world matrix may
        # only have been changed at a top hierarchy object and all
        # the children still need their world matrices updated.
        viewlayer.Update()

        self.xBoundBox.Move(vDelta)

    # enddef

    # #################################################################################################
    def RotateEuler(
        self,
        *,
        _lEulerAngles: list[float] = None,
        _bAnglesInDeg: bool = True,
        _lOriginOffset: list[float] = [0.0, 0.0, 0.0],
    ) -> mathutils.Matrix:
        matTrans = self.xBoundBox.GetRotateEulerMatrix(
            _lEulerAngles=_lEulerAngles, _bAnglesInDeg=_bAnglesInDeg, _lOriginOffset=_lOriginOffset
        )

        for sObjName in self._lObjects:
            objX = bpy.data.objects.get(sObjName)
            if objX is None:
                raise RuntimeError(f"Object '{sObjName}' not available")
            # endif
            objX.matrix_world = matTrans @ objX.matrix_world
        # endfor

        # Need to update the viewlayer, since the world matrix may
        # only have been changed at a top hierarchy object and all
        # the children still need their world matrices updated.
        viewlayer.Update()

        # Re-evaluate bounding box to ensure z-axis is up.
        self.EvalBoundingBox()

        return matTrans

    # enddef

    # #################################################################################################
    def GetParentCollection(self) -> bpy.types.Collection:
        return collection.FindParentCollectionOfCollection(bpy.context, self.xCollection)

    # enddef

    # #################################################################################################
    def ParentTo(self, _sParentObject: str, _bKeepTransform: bool = True, _bKeepRelTransform: bool = False):
        objParent: bpy.types.Object = bpy.data.objects.get(_sParentObject)
        if objParent is None:
            raise RuntimeError(f"Parent object '{_sParentObject}' not found")
        # endif

        lObjects = collection.GetCollectionObjects(self.xCollection, _bChildren=False, _bRecursive=True)

        for sObjName in lObjects:
            objX = bpy.data.objects[sObjName]
            object.ParentObject(objParent, objX, bKeepTransform=_bKeepTransform, bKeepRelTransform=_bKeepRelTransform)
        # endfor

        # Need to update the viewlayer, since the world matrix may
        # only have been changed at a top hierarchy object and all
        # the children still need their world matrices updated.
        viewlayer.Update()

    # enddef


# endclass


# ################################################################################################
class CInstances:
    def __init__(self, *, _sName=None):
        self._dicElement: dict[str, _CInstance] = {}

        if _sName is None:
            self._sName = "Instances"
        else:
            self._sName = _sName
        # endif

    # enddef

    def __len__(self) -> int:
        return self.iElementCount

    # enddef

    def __getitem__(self, sKey: str) -> _CInstance:
        return self._dicElement.get(sKey)

    # enddef

    def __iter__(self) -> _CInstance:
        for xInst in self._dicElement.values():
            yield xInst
        # endfor

    # enddef

    @property
    def iElementCount(self) -> int:
        return len(self._dicElement)

    # enddef

    @property
    def lNames(self) -> list[str]:
        return list(self._dicElement.keys())

    # enddef

    # ###################################################################################
    def AddCollectionElements(
        self, *, _clnX, _bChildCollectionsAsInstances: bool = False, _lObjectTypes: list[str] = None
    ):
        if _bChildCollectionsAsInstances is False:
            lObjects = collection.GetCollectionObjects(
                _clnX, _bChildren=False, _bRecursive=True, _lObjectTypes=_lObjectTypes
            )
            for sObjName in lObjects:
                self.AddObject(_sName=sObjName)
            # endfor

        else:
            lObjects = collection.GetCollectionObjects(
                _clnX, _bChildren=False, _bRecursive=False, _lObjectTypes=_lObjectTypes
            )
            for sObjName in lObjects:
                self.AddObject(_sName=sObjName)
            # endfor

            for clnChild in _clnX.children:
                self.AddCollection(_clnX=clnChild)
            # endfor
        # endif

    # enddef

    # ###################################################################################
    def AddElement(self, _xInstance: _CInstance):
        self._dicElement[_xInstance.sName] = _xInstance

    # enddef

    # ###################################################################################
    def AddCollection(self, *, _clnX, _lObjectTypes=None):
        self._dicElement[_clnX.name] = CCollectionInstance(_clnX=_clnX, _lObjectTypes=_lObjectTypes)

    # enddef

    # ###################################################################################
    def AddObject(self, *, _sName=None, _objX=None):
        if _sName is None:
            if _objX is None:
                raise RuntimeError("An object name or an object have to be given for initialization")
            # endif
            sName = _objX.name
        else:
            sName = _sName
        # endif

        if sName not in self._dicElement:
            self._dicElement[sName] = CObjectInstance(_sName=_sName)
        # endif

    # enddef

    # ###################################################################################
    def CreateRandomInstances(
        self,
        *,
        _iInstanceCount,
        _bLinked=True,
        _sName=None,
        _funcGetTargetCollection: Optional[Callable[[_CInstance, bpy.types.Collection], bpy.types.Collection]] = None,
        _funcProcInstance: Optional[Callable[[_CInstance, bpy.types.Collection], None]] = None,
    ) -> "CInstances":
        if _iInstanceCount <= 0:
            raise RuntimeError(f"Invalid instance count '{_iInstanceCount}'")
        # endif

        iIdx = 1
        sName = _sName
        while sName in bpy.data.collections:
            sName = f"{_sName} {iIdx}"
            iIdx += 1
        # endwhile

        xCtx = bpy.context
        clnRoot = collection.GetRootCollection(xCtx)
        clnParentInst = collection.CreateCollection(xCtx, sName, clnParent=clnRoot)

        # The new instance collection
        xInstCln = CInstances(_sName=_sName)
        lElKeys = list(self._dicElement.keys())
        iElCnt = len(lElKeys)

        # For small lists of elements, the random.choice() function
        # selection can be very biased. The following process avoids
        # that two consecutive random values are the same.
        # This gives a more even mix of all source objects.
        lSelIdx = [random.randrange(0, iElCnt)]
        for iIdx in range(_iInstanceCount - 1):
            while True:
                iElIdx = random.randrange(0, iElCnt)
                if iElIdx != lSelIdx[iIdx] or iElCnt == 1:
                    break
                # endif
            # endwhile
            lSelIdx.append(iElIdx)
        # endfor
        # print(lSelKeys)

        for iElIdx in lSelIdx:
            sElKey = lElKeys[iElIdx]
            # print(f"Random instance choice: {sElKey}")
            xInst: _CInstance = self._dicElement[sElKey]
            xInstCopy: _CInstance = None

            if _funcGetTargetCollection is not None:
                clnInst = _funcGetTargetCollection(xInst, clnParentInst)
                xInstCopy = xInst.Copy(_bLinked=_bLinked, _clnTarget=clnInst)
            else:
                xInstCopy = xInst.Copy(_bLinked=_bLinked, _clnTarget=clnParentInst)
            # endif

            if _funcProcInstance is not None:
                _funcProcInstance(xInstCopy, clnParentInst)
            # endif

            xInstCln.AddElement(xInstCopy)

        # endfor

        return xInstCln

    # enddef

    # # ###################################################################################
    # def RandomRotate(
    #     self,
    #     *,
    #     _lEulerRanges: list[list[float]] = None,
    #     _bAnglesInDeg: bool = True,
    #     _lOriginOffset: list[float] = [0.0, 0.0, 0.0],
    # ):

    #     for xInst in self._dicElement.values():
    #         vRotCtr = _lOriginOffset[0] * xInst.xBoundBox.lBase[0]


# endclass
