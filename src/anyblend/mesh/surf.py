#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /surf.py
# Created Date: Thursday, October 22nd 2020, 1:20:30 pm
# Author: Christian Perwass
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


def CreateVexFaceLists(_lGrid, _dScale, _bNormUp):

    iRowCnt = len(_lGrid)
    iColCnt = len(_lGrid[0])

    lVex = [
        tuple(_lGrid[iRow][iCol] * _dScale)
        for iRow in range(iRowCnt)
        for iCol in range(iColCnt)
    ]

    if _bNormUp:
        lFace = [
            (
                iRow * iColCnt + iCol,
                iRow * iColCnt + iCol + 1,
                (iRow + 1) * iColCnt + iCol + 1,
                (iRow + 1) * iColCnt + iCol,
            )
            for iRow in range(iRowCnt - 1)
            for iCol in range(iColCnt - 1)
        ]
    else:
        lFace = [
            (
                iRow * iColCnt + iCol,
                (iRow + 1) * iColCnt + iCol,
                (iRow + 1) * iColCnt + iCol + 1,
                iRow * iColCnt + iCol + 1,
            )
            for iRow in range(iRowCnt - 1)
            for iCol in range(iColCnt - 1)
        ]
    # endif

    return {"iRowCnt": iRowCnt, "iColCnt": iColCnt, "lVex": lVex, "lFace": lFace}


# enddef


def CreateSurf(_sName, _lGrid, _dMeterPerUnit, _bNormUp=True):

    dScale = _dMeterPerUnit / bpy.context.scene.unit_settings.scale_length

    dicData = CreateVexFaceLists(_lGrid, dScale, _bNormUp)

    # Create Mesh Datablock
    mesh = bpy.data.meshes.new(_sName)
    mesh.from_pydata(dicData["lVex"], [], dicData["lFace"])

    # Create Object and link to scene
    obj = bpy.data.objects.new(_sName, mesh)
    bpy.context.collection.objects.link(obj)


# enddef


def CreateSurf2(_sName, _lGrid1, _lGrid2, _lLocation, _sMaterial, _dMeterPerUnit):

    dScale = _dMeterPerUnit / bpy.context.scene.unit_settings.scale_length

    dicSurf1 = CreateVexFaceLists(_lGrid1, dScale, True)
    dicSurf2 = CreateVexFaceLists(_lGrid2, dScale, False)

    lVex = dicSurf1["lVex"]
    iVexCnt1 = len(lVex)

    lVex.extend(dicSurf2["lVex"])

    lFace = dicSurf1["lFace"]

    lFace2 = [
        (tF[0] + iVexCnt1, tF[1] + iVexCnt1, tF[2] + iVexCnt1, tF[3] + iVexCnt1)
        for tF in dicSurf2["lFace"]
    ]
    lFace.extend(lFace2)

    iRowCnt1 = dicSurf1["iRowCnt"]
    iColCnt1 = dicSurf1["iColCnt"]
    iRowCnt2 = dicSurf2["iRowCnt"]
    iColCnt2 = dicSurf2["iColCnt"]

    lSide = [
        (iVexCnt1 + iCol, iVexCnt1 + iCol + 1, iCol + 1, iCol)
        for iCol in range(iColCnt1 - 1)
    ]
    lFace.extend(lSide)

    iOff = (iRowCnt1 - 1) * iColCnt1
    lSide = [
        (
            iOff + iCol,
            iOff + iCol + 1,
            iOff + iVexCnt1 + iCol + 1,
            iOff + iVexCnt1 + iCol,
        )
        for iCol in range(iColCnt1 - 1)
    ]
    lFace.extend(lSide)

    lSide = [
        (
            iRow * iColCnt1,
            (iRow + 1) * iColCnt1,
            iVexCnt1 + (iRow + 1) * iColCnt1,
            iVexCnt1 + iRow * iColCnt1,
        )
        for iRow in range(iRowCnt1 - 1)
    ]
    lFace.extend(lSide)

    iOff = iColCnt1 - 1
    lSide = [
        (
            iOff + iVexCnt1 + (iRow) * iColCnt1,
            iOff + iVexCnt1 + (iRow + 1) * iColCnt1,
            iOff + (iRow + 1) * iColCnt1,
            iOff + (iRow) * iColCnt1,
        )
        for iRow in range(iRowCnt1 - 1)
    ]
    lFace.extend(lSide)

    # Create Mesh Datablock
    mesh = bpy.data.meshes.new(_sName)
    mesh.from_pydata(lVex, [], lFace)
    for xFace in mesh.polygons:
        xFace.use_smooth = True
    # endfor

    # Create Object and link to scene
    obj = bpy.data.objects.new(_sName, mesh)
    obj.location = tuple([dScale * x for x in _lLocation])

    if len(_sMaterial) > 0:
        matWS = bpy.data.materials.get(_sMaterial)
        obj.data.materials.append(matWS)
    # endif

    bpy.context.collection.objects.link(obj)
    # bpy.context.scene.objects.link(obj)


# enddef
