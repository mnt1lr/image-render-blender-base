#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_polygons.py
# Created Date: Tuesday, November 1st 2022, 8:27:42 am
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
import random
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple
from collections.abc import Iterable

from anybase import assertion

from anyblend import object


@dataclass
class CObjectData:
    sName: str = None
    lWeights: list[float] = None
    lPoly: list[list[int]] = None
    aVex: np.ndarray = None
    fMaxWeight: float = None


# endclass


class CPolygons:
    def __init__(self):
        self._lObjects: list[CObjectData] = []
        self._dicObjects: dict[str, int] = {}
        self._iTotalPolyCount: int = 0
        self._lAccumPolyCount: list[int] = []
        self._fMaxWeight: float = 0.0
        self._aDistribution: np.ndarray = None

    # enddef

    # ####################################################################################
    @property
    def iTotalPolyCount(self) -> int:
        return self._iTotalPolyCount

    # enddef

    @property
    def fMaxWeight(self) -> float:
        return self._fMaxWeight

    # enddef

    @property
    def lObjectVertexIndices(self) -> Iterable[tuple[int, CObjectData]]:
        for xObjData in self._lObjects:
            iVexCnt = len(xObjData.lWeights)
            for iVexIdx in range(iVexCnt):
                yield iVexIdx, xObjData
            # endfor
        # endfor

    # enddef

    # ####################################################################################
    def _Update(self):
        self._iTotalPolyCount = 0
        self._lAccumPolyCount = [0]
        for xData in self._lObjects:
            iPolyCnt = len(xData.lPoly)
            self._iTotalPolyCount += iPolyCnt
            self._lAccumPolyCount.append(self._iTotalPolyCount)
        # endfor

    # enddef

    # ####################################################################################
    def _GetObjectPolyIdx(self, _iAbsPolyIdx) -> Tuple[int, CObjectData]:
        if _iAbsPolyIdx < 0:
            raise RuntimeError(f"Polynomial index '{_iAbsPolyIdx}' out of range")
        # endif

        for iObjIdx in range(1, len(self._lAccumPolyCount)):
            if _iAbsPolyIdx < self._lAccumPolyCount[iObjIdx]:
                iObjPolyIdx = _iAbsPolyIdx - self._lAccumPolyCount[iObjIdx - 1]
                xData = self._lObjects[iObjIdx - 1]
                return iObjPolyIdx, xData
            # endif
        # endfor

        print(f"_iAbsPolxIdx: {_iAbsPolyIdx}")
        print(f"_Accum: {self._lAccumPolyCount}")

        raise RuntimeError(f"Polynomial index '{_iAbsPolyIdx}' out of range")

    # enddef

    # ####################################################################################
    def GetPolyVertices(self, _iAbsPolyIdx: int) -> np.ndarray:
        iPolyIdx, xData = self._GetObjectPolyIdx(_iAbsPolyIdx)
        lVexIdx = xData.lPoly[iPolyIdx]
        return xData.aVex[lVexIdx]

    # enddef

    # ####################################################################################
    def GetPolyWeight(self, _iAbsPolyIdx: int) -> np.ndarray:
        iPolyIdx, xData = self._GetObjectPolyIdx(_iAbsPolyIdx)
        lVexIdx = xData.lPoly[iPolyIdx]
        fWeight = sum([xData.lWeights[i] for i in lVexIdx]) / len(lVexIdx)
        return fWeight

    # enddef

    # ####################################################################################
    def GetRandomPosOnPoly(self, _iAbsPolyIdx: int) -> np.ndarray:
        iPolyIdx, xData = self._GetObjectPolyIdx(_iAbsPolyIdx)
        lVexIdx = xData.lPoly[iPolyIdx]
        aVex = xData.aVex[lVexIdx]
        lWeights = [xData.lWeights[i] * random.uniform(0.01, 1.0) for i in lVexIdx]
        aWeights = np.array(lWeights).reshape(len(lWeights), 1)

        aVex = aVex * aWeights
        aVex = np.sum(aVex, axis=0) / np.sum(aWeights)

        return aVex

    # enddef

    # ####################################################################################
    def GetRandomPosOnPolyUniformlySimplex(self, _iAbsPolyIdx: int) -> np.ndarray:
        # https://cs.stackexchange.com/questions/3227/uniform-sampling-from-a-simplex

        iPolyIdx, xData = self._GetObjectPolyIdx(_iAbsPolyIdx)
        lVexIdx = xData.lPoly[iPolyIdx]
        aVex = xData.aVex[lVexIdx]
        aCalculateProbs = np.zeros(len(lVexIdx) + 1)
        aCalculateProbs[1:-1] = np.sort(np.random.uniform(size=(len(lVexIdx) - 1)))
        aCalculateProbs[-1] = 1
        aProbs = aCalculateProbs[1:] - aCalculateProbs[:-1]
        aWeights = np.array([xData.lWeights[i] for i in lVexIdx])
        aVex = aVex * aProbs[:, None] * aWeights[:, None]
        aVex = np.sum(aVex, axis=0) / np.sum(aProbs * aWeights)

        return aVex

    # enddef

    # ####################################################################################
    def _CalcWeightAndAreaDistribution(self):
        lAreas = []
        lWeights = []
        for xData in self._lObjects:
            for lVexIdx in xData.lPoly:
                lPairwiseDistances = []

                lVexPairs = []
                for i, iVexId1 in enumerate(lVexIdx):
                    for iVexId2 in lVexIdx[i + 1 :]:
                        lVexPairs.append((iVexId1, iVexId2))
                    # endfor
                # endfor

                for iVexId1, iVexId2 in lVexPairs:
                    aVecSub = xData.aVex[iVexId1] - xData.aVex[iVexId2]
                    lPairwiseDistances.append(np.linalg.norm(aVecSub))
                # endfor

                iAreaApprox = (
                    np.min(lPairwiseDistances)
                    * np.median(lPairwiseDistances)
                    * (0.5 if len(lPairwiseDistances) == 3 else 1)
                )

                lAreas.append(iAreaApprox)
                lWeights.append(sum([xData.lWeights[i] for i in lVexIdx]) / len(lVexIdx))
            # endfor
        # endfor

        aAreas = np.array(lAreas)
        aWeights = np.array(lWeights)

        aCumSum = np.cumsum(aAreas * aWeights)
        self._aDistribution = aCumSum / aCumSum[-1]

    # enddef

    # ####################################################################################
    def SampleUniformlyByWeightAndArea(self) -> np.ndarray:
        if self._aDistribution is None:
            self._CalcWeightAndAreaDistribution()
        # endif

        iPolyId = np.argmax(np.random.uniform() < self._aDistribution)
        return self.GetRandomPosOnPolyUniformlySimplex(iPolyId)
        # return self.GetRandomPosOnPoly(iPolyId)

    # enddef

    # ####################################################################################
    def AddFromObject(self, *, _sObjectName: str, _sVexGrpName: Optional[str] = None) -> bool:
        """Add polygons from a Blender mesh object

        Parameters
        ----------
        _sObjectName : str
            Name of the Blender object.

        _sVexGrpName : str (optional)
            Name of the vertex group that contains the vertex weights.
            If 'None', uses equal unit weights.

        Raises
        ------
        RuntimeError
            Invalid object type, or object not found.
        """
        assertion.FuncArgTypes()

        if _sObjectName in self._dicObjects:
            raise RuntimeError(f"Object '{_sObjectName}' has already been added")
        # endif

        objOrig = bpy.data.objects.get(_sObjectName)
        if objOrig is None:
            raise RuntimeError(f"Object '{_sObjectName}' not found")
        # endif

        if objOrig.type != "MESH":
            raise RuntimeError(f"Object '{_sObjectName}' is not a mesh object")
        # endif

        xData = CObjectData()
        xData.sName = _sObjectName

        # Get evaluated object
        xDG = bpy.context.evaluated_depsgraph_get()
        objEval = objOrig.evaluated_get(xDG)

        xData.aVex = object.GetMeshVex(objEval, sFrame="WORLD")
        if _sVexGrpName is None:
            xData.lWeights = [1.0 for i in range(xData.aVex.shape[0])]
        else:
            xData.lWeights = object.GetVertexWeights(objEval, _sVexGrpName)
        # endif

        mshEval = objEval.data
        xData.lPoly = []

        xData.fMaxWeight = 0.0
        for plyX in mshEval.polygons:
            lW = [xData.lWeights[i] for i in plyX.vertices]
            fMax = max(lW)
            xData.fMaxWeight = fMax if fMax > xData.fMaxWeight else xData.fMaxWeight

            fSum = sum(lW)
            if fSum > 0.0:
                xData.lPoly.append(list(plyX.vertices))
            # endif
        # endfor
        # print(f"lPoly: {xData.lPoly}")

        # Check if any polygons are left after weighting
        iPlyCnt = len(xData.lPoly)
        if iPlyCnt == 0:
            return False
        # endif

        self._fMaxWeight = max(self._fMaxWeight, xData.fMaxWeight)

        self._dicObjects[_sObjectName] = len(self._lObjects)
        self._lObjects.append(xData)

        self._Update()
        return True

    # enddef


# endclass
