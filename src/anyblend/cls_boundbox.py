#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_boundbox.py
# Created Date: Tuesday, November 1st 2022, 10:41:10 am
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
import math
import numpy as np
from anybase import assertion
from anyblend import object, collection


class CBoundingBox:
    def __init__(
        self,
        *,
        _objX=None,
        _lObjects: list = None,
        _bLocal: bool = False,
        _bCompoundObject: bool = True,
        _bUseMesh: bool = False,
    ):

        if _objX is None and _lObjects is not None:
            self._InitFromObjectList(
                _lObjects=_lObjects, _bLocal=_bLocal, _bCompoundObject=_bCompoundObject, _bUseMesh=_bUseMesh
            )

        elif _objX is not None and _lObjects is None:
            self._InitFromObjectList(
                _lObjects=[_objX], _bLocal=_bLocal, _bCompoundObject=_bCompoundObject, _bUseMesh=_bUseMesh
            )

        else:
            raise RuntimeError("Invalid initialization of bounding box instance")
        # endif

    # enddef

    # ##############################################################################
    def _EvalBoundingBox(self, *, _lPoints: list = None, _aVertices: np.ndarray = None):

        # Use an SVD to determine the main directions of the vertex set

        if _lPoints is not None:
            aVex = np.array(_lPoints)
        else:
            aVex = _aVertices
        # endif

        aMean = np.mean(aVex, axis=0)
        aRelVex = aVex - aMean

        # Always take axis [0,0,1] as the upward axis of the bounding box.
        # This will be the vZ or third axis in the basis.
        # Reduce the relative vertices to the xy-plane, to then evaluate
        # the main axes in that plane.
        aRelVex2d = aRelVex[:, 0:2]

        aSqVex2d = aRelVex2d.transpose() @ aRelVex2d
        mWorldInvT2d, mS, mWorldT2d = np.linalg.svd(aSqVex2d)

        mWorldInvT = np.zeros((3, 3))
        mWorldInvT[0:2, 0:2] = mWorldInvT2d
        mWorldInvT[2, 2] = 1.0
        # print(mWorldInvT)

        mWorldT = np.zeros((3, 3))
        mWorldT[0:2, 0:2] = mWorldT2d
        mWorldT[2, 2] = 1.0
        # print(mWorldT)

        # Transform vertices into main axis frame
        aRotVex = aVex @ mWorldInvT

        aMin = aRotVex.min(axis=0)
        aMax = aRotVex.max(axis=0)
        aSize = aMax - aMin
        aCtr = (aMin + aSize / 2.0) @ mWorldT

        self._tSize = tuple(aSize.tolist())
        self._tHalfSize = tuple([x / 2.0 for x in self._tSize])
        self._fRadius = math.sqrt(sum([x * x / 4.0 for x in self._tSize]))

        self._vCenter = mathutils.Vector(tuple(aCtr.tolist()))
        self._lBase = [
            mathutils.Vector(tuple(mWorldT[0].tolist())),
            mathutils.Vector(tuple(mWorldT[1].tolist())),
            mathutils.Vector(tuple(mWorldT[2].tolist())),
        ]

        self._lCorners = [
            mathutils.Vector(np.array([aMin[0], aMin[1], aMin[2]]) @ mWorldT),
            mathutils.Vector(np.array([aMin[0], aMin[1], aMax[2]]) @ mWorldT),
            mathutils.Vector(np.array([aMin[0], aMax[1], aMax[2]]) @ mWorldT),
            mathutils.Vector(np.array([aMin[0], aMax[1], aMin[2]]) @ mWorldT),
            mathutils.Vector(np.array([aMax[0], aMin[1], aMin[2]]) @ mWorldT),
            mathutils.Vector(np.array([aMax[0], aMin[1], aMax[2]]) @ mWorldT),
            mathutils.Vector(np.array([aMax[0], aMax[1], aMax[2]]) @ mWorldT),
            mathutils.Vector(np.array([aMax[0], aMax[1], aMin[2]]) @ mWorldT),
        ]

        vA = self._lCorners[0]
        vB = self._lCorners[6]
        self._vCornerMin: mathutils.Vector = mathutils.Vector((min(vA[0], vB[0]), min(vA[1], vB[1]), min(vA[2], vB[2])))

    # enddef

    # ##############################################################################
    def CreateBlenderObject(self, *, _sName: str, _bReplace: bool = True, _xCollection=None):

        objX = bpy.data.objects.get(_sName)
        if objX is not None and _bReplace is True:
            bpy.data.objects.remove(objX)
            objX = None
        # endif

        if _xCollection is None:
            xCln = collection.GetActiveCollection(bpy.context)
        else:
            xCln = _xCollection
        # endif

        objX = object.CreateObject(bpy.context, _sName, xCollection=xCln)

        mshX = objX.data

        lEdges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]

        mshX.from_pydata(self._lCorners, lEdges, [])
        mshX.update(calc_edges=True)
        objX.matrix_world = mathutils.Matrix.Identity(4)
        objX.location = mathutils.Vector((0.0, 0.0, 0.0))

        return objX

    # enddef

    # ##############################################################################
    def _InitFromObjectList(
        self, *, _lObjects: list, _bLocal: bool, _bCompoundObject: bool = True, _bUseMesh: bool = False
    ):
        self._bLocal = _bLocal

        setObjNames = set([x.name for x in _lObjects])

        if _bCompoundObject is True:
            for objX in _lObjects:
                lChildren = object.GetObjectChildrenNames(objX, bRecursive=True)
                for sChild in lChildren:
                    setObjNames.add(sChild)
                # endfor
            # endfor
        # endif

        lC = []
        if self._bLocal is True:
            for sObjName in setObjNames:
                objX = bpy.data.objects[sObjName]
                if _bUseMesh is True:
                    lC.append(object.GetMeshVex(objX, sFrame="LOCAL", bEvaluated=True))
                else:
                    lC.extend(mathutils.Vector(x) for x in objX.bound_box)
                # endif
            # endfor
        else:
            for sObjName in setObjNames:
                objX = bpy.data.objects[sObjName]
                if _bUseMesh is True:
                    lC.append(object.GetMeshVex(objX, sFrame="WORLD", bEvaluated=True))
                else:
                    lC.extend(objX.matrix_world @ mathutils.Vector(x) for x in objX.bound_box)
                # endif
            # endfor
        # endif

        if _bUseMesh is True:
            aVex = np.concatenate(lC, axis=0)
            self._EvalBoundingBox(_aVertices=aVex)

        else:
            self._EvalBoundingBox(_lPoints=lC)
        # endif

    # enddef

    # # ##############################################################################
    # def _InitFromObject(self, *, _objX, _bLocal: bool):
    #     self._bLocal = _bLocal

    #     if self._bLocal is True:
    #         lC = [mathutils.Vector(x) for x in _objX.bound_box]
    #     else:
    #         lC = [_objX.matrix_world @ mathutils.Vector(x) for x in _objX.bound_box]
    #     # endif

    #     self._EvalBoundingBox(_lPoints=lC)

    #     # self._lBase = [
    #     #     lC[4] - lC[0],
    #     #     lC[3] - lC[0],
    #     #     lC[1] - lC[0],
    #     # ]

    #     # self._tSize = tuple([x.length for x in self._lBase])
    #     # self._tHalfSize = tuple([x / 2.0 for x in self._tSize])
    #     # self._lBase = [x.normalized() for x in self._lBase]

    #     # self._fRadius = math.sqrt(sum([x * x / 4.0 for x in self._tSize]))

    #     # self._vCenter = mathutils.Vector((0, 0, 0))
    #     # for vA in lC:
    #     #     self._vCenter += vA
    #     # # endfor
    #     # self._vCenter /= 8.0

    #     # self._lCorners = lC

    # # enddef

    @property
    def lCorners(self):
        return self._lCorners

    # enddef

    @property
    def vCornerMin(self):
        return self._vCornerMin

    # enddef

    @property
    def vX(self):
        return self._lBase[0]

    # enddef

    @property
    def vY(self):
        return self._lBase[1]

    # enddef

    @property
    def vZ(self):
        return self._lBase[2]

    # enddef

    @property
    def lBase(self):
        return self._lBase.copy()

    # enddef

    @property
    def vCenter(self):
        return self._vCenter

    # enddef

    @property
    def tSize(self):
        return self._tSize

    # enddef

    @property
    def fSizeX(self):
        return self._tSize[0]

    # enddef

    @property
    def fSizeY(self):
        return self._tSize[1]

    # enddef

    @property
    def fSizeZ(self):
        return self._tSize[2]

    # enddef

    @property
    def tHalfSize(self):
        return self._tHalfSize

    # enddef

    @property
    def fHalfSizeX(self):
        return self._tHalfSize[0]

    # enddef

    @property
    def fHalfSizeY(self):
        return self._tHalfSize[1]

    # enddef

    @property
    def fHalfSizeZ(self):
        return self._tHalfSize[2]

    # enddef

    @property
    def fRadius(self):
        return self._fRadius

    # enddef

    # ######################################################################################
    def Move(self, _xDelta):
        vDelta = mathutils.Vector(_xDelta)
        self._vCenter += vDelta
        for vC in self._lCorners:
            vC += vDelta
        # endfor

    # enddef

    # #################################################################################################
    def GetDelta(self, _lRelDelta: list[float]):

        assertion.IsList(_lRelDelta, sMsg="Relative position must be list of three floats")
        assertion.IsTrue(len(_lRelDelta) == 3, sMsg="Relative position must be list of three floats")

        vDelta = mathutils.Vector((0, 0, 0))
        for i in range(3):
            vDelta += _lRelDelta[i] * self._tSize[i] * self._lBase[i]
        # endfor

        return vDelta

    # enddef

    # #################################################################################################
    def GetRotateEulerMatrix(
        self,
        *,
        _lEulerAngles: list[float] = None,
        _bAnglesInDeg: bool = True,
        _lOriginOffset: list[float] = [0.0, 0.0, 0.0],
    ) -> mathutils.Matrix:

        if _bAnglesInDeg is True:
            lAngles = [math.radians(x) for x in _lEulerAngles]
        else:
            lAngles = _lEulerAngles
        # endif

        vRotCtr = self.vCenter
        for i in range(3):
            vRotCtr += _lOriginOffset[i] * self.tSize[i] * self.lBase[i]
        # endfor

        matT = mathutils.Matrix.Translation(-vRotCtr)
        matR = mathutils.Euler(lAngles, "XYZ").to_matrix().to_4x4()

        matTrans = matT.inverted() @ matR @ matT

        return matTrans

    # enddef

    # #################################################################################################
    def RotateEuler(
        self,
        *,
        _lEulerAngles: list[float] = None,
        _bAnglesInDeg: bool = True,
        _lOriginOffset: list[float] = [0.0, 0.0, 0.0],
    ) -> mathutils.Matrix:

        matTrans = self.GetRotateEulerMatrix(
            _lEulerAngles=_lEulerAngles, _bAnglesInDeg=_bAnglesInDeg, _lOriginOffset=_lOriginOffset
        )

        self._vCenter = (matTrans @ self._vCenter.to_4d()).to_3d()
        matTrans3 = matTrans.to_3x3()
        for i in range(len(self._lBase)):
            self._lBase[i] = matTrans3 @ self._lBase[i]
        # endfor

        for i in range(len(self._lCorners)):
            self._lCorners[i] = (matTrans @ self._lCorners[i].to_4d()).to_3d()
        # endfor

        return matTrans

    # enddef

    # ######################################################################################
    def IsAnyPointInside(self, _lPoints: list[mathutils.Vector], *, _fBorder: float = 0.0):
        bIntersect = False
        for vPnt in _lPoints:
            vA = vPnt - self._vCenter

            if all(abs(vA.dot(x)) <= self._tHalfSize[i] + _fBorder for i, x in enumerate(self._lBase)):
                bIntersect = True
                break
            # endif
        # endfor

        return bIntersect

    # enddef

    # ######################################################################################
    def AllPointsInside(self, _lPoints: list[mathutils.Vector], *, _fBorder: float = 0.0):
        bInside = True
        for vPnt in _lPoints:
            vA = vPnt - self._vCenter

            if not all(abs(vA.dot(x)) <= self._tHalfSize[i] + _fBorder for i, x in enumerate(self._lBase)):
                bInside = False
                break
            # endif
        # endfor

        return bInside

    # enddef

    # ######################################################################################
    def AllPointsToOneSideOfBoundBox(self, _lPoints: list[mathutils.Vector]):
        bOutside = False
        for iIdx, vDir in enumerate(self._lBase):
            lSep = [(x - self._vCenter).dot(vDir) for x in _lPoints]
            # print(f"{vDir} -> {lSep}")
            if all(x > self._tHalfSize[iIdx] for x in lSep) or all(x < -self._tHalfSize[iIdx] for x in lSep):
                bOutside = True
                break
            # endif
        # endfor

        # print(f"bOutside: {bOutside}")
        return bOutside

    # enddef

    # ######################################################################################
    @staticmethod
    def TestIntersect(_xBoxA: "CBoundingBox", _xBoxB: "CBoundingBox"):

        # If the two boxes' centers are farther away that the sum
        # of the radii of their enclosing spheres, they cannot intersect.
        # This saves the more computationally expensive plane test below.
        fDist = (_xBoxA.vCenter - _xBoxB.vCenter).length
        if fDist > _xBoxA.fRadius + _xBoxB.fRadius:
            return False
        # endif

        # if all corner points of one bounding box are on the outside
        # of one of the side planes of the other bounding box, then
        # the boxes do not intersect. Need to test in both directions.
        if _xBoxA.AllPointsToOneSideOfBoundBox(_xBoxB.lCorners) is True:
            return False
        elif _xBoxB.AllPointsToOneSideOfBoundBox(_xBoxA.lCorners) is True:
            return False
        # endif

        return True

    # enddef

    # ######################################################################################
    def Intersects(self, _xBox: "CBoundingBox"):
        return CBoundingBox.TestIntersect(self, _xBox)

    # enddef

    # ######################################################################################
    def IsInside(self, _xBox: "CBoundingBox", *, _fBorder: float = 0.0):
        return _xBox.AllPointsInside(self.lCorners, _fBorder=_fBorder)

    # enddef

    # ######################################################################################
    def IsOutside(self, _xBox: "CBoundingBox", _fBorder: float = 0.0):
        return not _xBox.IsAnyPointInside(self.lCorners, _fBorder=_fBorder)

    # enddef

    # ######################################################################################
    def EvalObjectRelation(self, _objX, *, _fBorder: float = 0.0) -> str:

        if _objX.type != "MESH":
            raise RuntimeError("Testing object inside bounding box only implemented for mesh objects")
        # endif

        aVex = object.GetMeshVex(_objX, sFrame="WORLD", bEvaluated=True)
        aRelVex = aVex - np.array(list(self.vCenter))

        lBase = [np.array(list(x)).reshape(1, 3) for x in self.lBase]
        aBase: np.ndarray = np.concatenate(lBase, axis=0)

        aLocVex = np.abs(aRelVex @ aBase.T)
        aVexDist = np.max(aLocVex, axis=0)
        aSize = np.array(self.tHalfSize) + _fBorder
        aInside = aVexDist <= aSize
        aOutside = aVexDist > aSize

        bInside = np.alltrue(aInside).item()
        bOutside = np.alltrue(aOutside).item()

        sResult = None
        if bInside is True:
            sResult = "INSIDE"
        elif bOutside is True:
            sResult = "OUTSIDE"
        else:
            sResult = "INTERSECT"
        # endif

        # print(f"{_objX.name}: {sResult}, {aVexDist}, {aSize}, {aInside}, {aOutside}, {bInside}, {bOutside}")

        return sResult

    # endif

    # ######################################################################################
    def IsObjectInside(self, _objX, *, _fBorder: float = 0.0):
        return self.EvalObjectRelation(_objX, _fBorder=_fBorder) == "INSIDE"

    # enddef

    # ######################################################################################
    def IsObjectOutside(self, _objX, *, _fBorder: float = 0.0):
        return self.EvalObjectRelation(_objX, _fBorder=_fBorder) == "OUTSIDE"

    # enddef

    # ######################################################################################
    def IsObjectIntersect(self, _objX, *, _fBorder: float = 0.0):
        return self.EvalObjectRelation(_objX, _fBorder=_fBorder) == "INTERSECT"

    # enddef


# endclass
