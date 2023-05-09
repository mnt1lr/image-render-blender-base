#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \tools.py
# Created Date: Tuesday, December 6th 2022, 10:36:57 am
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

import random

from anyblend.cls_boundbox import CBoundingBox
from . import collection
from . import viewlayer
from . import object as anyobj
from . import ops_object as anyops


############################################################################################
def GetRandomColor() -> list[float]:
    lColor = [random.uniform(0.0, 1.0) for i in range(3)]
    fMax = max(lColor)
    return [round(x / fMax, 3) for x in lColor]


# enddef

############################################################################################
def SpreadObjectsIn2D(
    _sClnTop: str,
    *,
    _lOffset: list[float] = None,
    _lfRelDelta: list[float] = [2.0, 0.1, 0.2],
    _lDirList: list[list[float]] = None,
    _iMaxColCnt: int = None,
    _bShowRowTitles: bool = False,
    _fRowTitleSize: float = 1.0,
):

    clnTop = bpy.data.collections.get(_sClnTop)
    if clnTop is None:
        raise RuntimeError(f"Collection '{_sClnTop}' does not exist")
    # endif

    # Order: Row, Column, Z
    lvDir: list[mathutils.Vector] = [
        mathutils.Vector((1, 0, 0)),
        mathutils.Vector((1, 1, 0)),
        mathutils.Vector((0, 0, 1)),
    ]

    if isinstance(_lDirList, list):
        if len(_lDirList) != 3:
            raise RuntimeError("List of directions must contain three lists of three floats each: {_lDir}")
        # endif

        for iDirIdx, lDir in enumerate(_lDirList):
            if not isinstance(lDir, list) or len(lDir) != 3:
                raise RuntimeError("List of directions must contain three lists of three floats each: {_lDir}")
            # endif
            lvDir[iDirIdx] = mathutils.Vector(lDir)
        # endfor

    # endif

    lvDir = [v.normalized() for v in lvDir]

    lRowClnNames = [x.name for x in clnTop.children]

    iMaxObjCnt: int = 0
    lMaxObjSize: list[float] = [0.0, 0.0, 0.0]
    dicObjects: dict[str, list[str]] = {}
    for sRowClnName in lRowClnNames:
        lObjList = collection.GetCollectionObjects(bpy.data.collections[sRowClnName], _bRecursive=True)
        dicObjects[sRowClnName] = lObjList
        iMaxObjCnt = max(iMaxObjCnt, len(lObjList))

        sObjName: str
        for sObjName in lObjList:
            objX = bpy.data.objects[sObjName]
            boxObj = CBoundingBox(_objX=objX, _bUseMesh=True)
            lSize = []
            for i in range(3):
                vDir = lvDir[i]
                lCorners: list[float] = [v.dot(vDir) for v in boxObj.lCorners]
                lSize.append(max(lCorners) - min(lCorners))
            # endfor

            lMaxObjSize = [max(lMaxObjSize[i], lSize[i]) for i in range(3)]
        # endfor
    # endfor

    lfDelta: list[float] = [(1.0 + _lfRelDelta[i]) * lMaxObjSize[i] for i in range(3)]

    vOrig: mathutils.Vector
    if not isinstance(_lOffset, list):
        vOrig = mathutils.Vector((0, 0, 0))
    else:
        if len(_lOffset) != 3:
            raise RuntimeError(f"Offset is not a list of three floats: {_lOffset}")
        # endif
        vOrig = mathutils.Vector(_lOffset)
    # endif

    if _iMaxColCnt is None or _iMaxColCnt <= 0:
        iMaxColCnt = iMaxObjCnt
    else:
        iMaxColCnt = _iMaxColCnt
    # endif

    for iRowIdx, sRowClnName in enumerate(lRowClnNames):
        lObjList = dicObjects[sRowClnName]
        vRowPos = vOrig + (iRowIdx + 0.5) * lfDelta[0] * lvDir[0]

        if _bShowRowTitles is True:
            clnRow = bpy.data.collections[sRowClnName]
            sTitle = sRowClnName
            if ";" in sTitle:
                sTitle = sTitle[sTitle.index(";") + 1 :]
            # endif

            objText = anyobj.CreateText(
                sTitle,
                _sName=f"Title.Row.{(iRowIdx+1):03d}",
                _sAlignX="RIGHT",
                _sAlignY="CENTER",
                _fSize=_fRowTitleSize,
                _xDir=lvDir[1],
                _xCollection=clnRow,
            )

            lColor = GetRandomColor()
            anyops.SetNewMaterial(objText, _lBaseColor=lColor, _lEmission=lColor)

            objText.location = vRowPos
        # endif

        for iObjIdx, sObjName in enumerate(lObjList):
            iColIdx = iObjIdx % iMaxColCnt
            iZIdx = iObjIdx // iMaxColCnt

            objX = bpy.data.objects[sObjName]

            vPos = vRowPos + (iColIdx + 0.5) * lfDelta[1] * lvDir[1] + (iZIdx + 0.5) * lfDelta[2] * lvDir[2]
            objX.location = vPos
        # endfor
    # endfor

    viewlayer.Update()


# enddef
