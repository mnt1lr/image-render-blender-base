#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \points.py
# Created Date: Tuesday, November 1st 2022, 8:44:02 am
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

import numpy as np
import copy
import math
import random
from typing import Optional, Union

from anyblend.cls_polygons import CPolygons
from anyblend.cls_boundbox import CBoundingBox
from anyblend.cls_instances import CInstances


######################################################
def GetRndPointsOnSurface(
    *,
    lTrgObjNames: list[str],
    iPntCnt: Optional[int] = None,
    fMinDist: float = 0.0,
    fMaxDist: float = math.inf,
    fMinHorizViewAngleSep_deg: float = 0.0,
    bUseCameraFov: bool = False,
    lCamFovBorder_deg: list[float] = [0.0, 0.0],
    lCamDistRange: list[float] = None,
    matCamWorld: Optional[mathutils.Matrix] = None,
    lCamFov_deg: Optional[list[float]] = None,
    lVexGrpNames: Optional[list[str]] = None,
    iSeed: Optional[int] = None,
    iMaxTrials: int = 20,
    xInstances: Optional[CInstances] = None,
    bUseBoundBox: bool = False,
    xInstanceOrigin: Union[list[float], str, None] = None,
    xObstacles: Optional[CInstances] = None,
) -> dict:
    """Create the given number of points at random positions on the surface.
       Takes into account the vertex weights of the given vertex group, if set.
       If instances are given to distribute on the surface, the delta to their
       current location is returned.

    Args:
        lTrgObjNames (str):
            A list of surface objects.

        iPntCnt (int):
            The number of points to generate

        fMinDist (float, optional):
            The minimal distance between points.
            If it is not possible to generate the given number of points
            due to this distance constraint, less points are returned.
            Defaults to 0.0.

        fMaxDist (float, optional):
            The maximal distance between points.
            If it is not possible to generate the given number of points
            due to this distance constraint, less points are returned.
            Defaults to math.inf.

        fMinHorizViewAngleSep_deg (float, optional, default=0.0):
            The minimal horizonal view angle separation in degrees of the generated points.
            The argumeent 'matCamWorld' must be specified.

        bUseCameraFov (bool, optional, default=false):
            Contraints points to the horizontal camera field of view if set to true.
            The arguments 'matCamWorld' and 'lCamFov_deg' must be specified.

        lCamFovBorder_deg (list[float], optional, default=[0.0, 0.0]):
            Only used when 'bUseCameraFov' is true.
            Specifies the horizontal and vertical FoV border around the actual camera FoV.

        lCamDistRange (list[float], optional, default=[0, inf]):
            Minimal and maximal distance from camera that are allowed.

        matCamWorld (mathutils.Matrix, optional, default=None):
            Only needed if 'fMinHorizViewAngleSep_deg' > 0 or 'bUseCameraFov' is true.
            Must be set to a 4x4 world matrix.

        lCamFov_deg (list[float], optional, default=None):
            Only needed 'bUseCameraFov' is true. Gives the camera's field of view.

        lVexGrpNames (list[str], optional):
            The name of the vertex group to use per element in lTrgObjNames.
            Points are distributed based on
            the "weight" defined for each vertex of this vertex group.
            In Blender use "Weight Paint" to draw these weights. Defaults to None.

        bUseBoundBox (bool, optional):
            If set to true, uses the bounding boxes of the objects passed in "lObjects"
            to determine their minimal distance. Defaults to false.

        xInstanceOrigin (list[float] or str, optional, default=[0,0,-0.5]):
            If it is a list it gives the origin of the instances' bounding box relative to their centers.
                For example, [0,0,-0.5] is the center of the bottom plane,
                and [0,0,0] is the center of the bounding box.
            If it is a string it can be one of the following:
                - "ORIG": uses the instance's origin for placement and not the bounding box

        xInstances (CInstances, optional):
            List of instances to distribute on surface. Must be given if "bUseBoundBox" is True.

        xObstacles (CInstances, optional):
            Only used when bUseBoundBox is true. Instances whose bounding boxes
            will not be intersected by the object's bounding boxes.

        iSeed (int, optional):
            The random seed to use. Defaults to None.

        iMaxTrials (int, optional):
            The maximal number of random trials to find a valid position
            for a point. Defaults to 20.

    Returns:
        list: A list of vectors of type mathutils.Vector, giving positions on the surface.
    """
    if iSeed is not None:
        random.seed(iSeed)
        np.random.seed(iSeed)
    # endif

    if fMaxDist is None:
        fMaxDist = math.inf
    # endif

    if iPntCnt is None and xInstances is None:
        raise RuntimeError("Neither point count nor list of objects is given")
    # endif

    if bUseBoundBox is True and xInstances is None:
        raise RuntimeError("If 'bUseBoundBox' is true, need to specify list of objects")
    # endif

    if lCamDistRange is None:
        lCamDistRange = [0.0, math.inf]
    # endif

    if isinstance(xInstances, CInstances):
        bHasInst = True
        lInstNames = xInstances.lNames
    else:
        bHasInst = False
        lInstNames = None
    # endif

    if iPntCnt is None:
        iPntCnt = len(xInstances)
    # endif

    sInstOrig = None
    lInstOrig = None
    if isinstance(xInstanceOrigin, str):
        sInstOrig = xInstanceOrigin
        if sInstOrig not in ["ORIG"]:
            raise RuntimeError(f"Instance origin string must be 'ORIG', but '{sInstOrig}' was given")
        # endif
    elif isinstance(xInstanceOrigin, list):
        lInstOrig = xInstanceOrigin
        if len(lInstOrig) != 3:
            raise RuntimeError("Instance origin list must be of length three")
        # endif
    else:
        raise RuntimeError(f"Invalid instance origin argument: {xInstanceOrigin}")
    # endif

    lMatrixWorld = []
    xPolys = CPolygons()

    for iIdx, sTrgObjName in enumerate(lTrgObjNames):
        sVexGrpName = None
        if isinstance(lVexGrpNames, list) and iIdx < len(lVexGrpNames) and isinstance(lVexGrpNames[iIdx], str):
            sVexGrpName = lVexGrpNames[iIdx]
        # endif
        xPolys.AddFromObject(_sObjectName=sTrgObjName, _sVexGrpName=sVexGrpName)
        lMatrixWorld.append(bpy.data.objects[sTrgObjName].matrix_world)
    # endfor

    bHasDistConstraint = fMinDist > 1e-7 or fMaxDist != math.inf
    bHasAngleConstraint = fMinHorizViewAngleSep_deg > 1e-6

    # If a minimal view angle is specified, get the active camera
    fMinHorizViewAngleSep_rad = None
    # fCamHorizFov_rad = None
    if bHasAngleConstraint is True or bUseCameraFov is True:
        if matCamWorld is None:
            raise RuntimeError("No camera world matrix given")
        # endif

        if bUseCameraFov is True and lCamFov_deg is None:
            raise RuntimeError("No horizontal camera field of view given")
        else:
            if abs(lCamFov_deg[0]) / 2.0 - lCamFovBorder_deg[0] <= 0.1:
                raise RuntimeError("Horizontal camera FoV border is too large")
            # endif
            if abs(lCamFov_deg[1]) / 2.0 - lCamFovBorder_deg[1] <= 0.1:
                raise RuntimeError("Vertical camera FoV border is too large")
            # endif
            lCamFov_rad = [math.radians(abs(x)) for x in lCamFov_deg]
            lCamMaxViewAngle_rad = [lCamFov_rad[i] / 2.0 - math.radians(lCamFovBorder_deg[i]) for i in range(2)]
        # endif

        fMinHorizViewAngleSep_rad = math.radians(abs(fMinHorizViewAngleSep_deg))
        matProjXZ = mathutils.Matrix.OrthoProjection("XZ", 3)
        matProjYZ = mathutils.Matrix.OrthoProjection("YZ", 3)
        matCamWorld_inv = matCamWorld.inverted()
        vCamOrig = matCamWorld.to_translation().to_3d()
    # endif

    # print(iPlyCnt)
    iPlyCnt = xPolys.iTotalPolyCount
    # print(iPlyCnt)

    dicPnts: dict[int, mathutils.Vector] = {}
    dicBoxes: dict[int, CBoundingBox] = {}
    lHorizViewDir = []
    vHorizViewDir_cam = None
    lPlyIdx: list[int] = list(range(0, iPlyCnt))

    for iPntIdx in range(0, iPntCnt):
        # print(f"Test point {iPntIdx}")
        vPos_w = None

        # Try to find a position as long as there are polynomials
        # to chose from
        while len(lPlyIdx) > 0:
            # Find a poly with a selection probability
            # defined the the vertex weights.
            for iTest in range(0, iMaxTrials):
                iPlyIdx = random.choice(lPlyIdx)

                fWeight = xPolys.GetPolyWeight(iPlyIdx)
                fRnd = random.uniform(0, xPolys.fMaxWeight)

                if fRnd < fWeight:
                    break
                # endif
            # endfor test

            # Evaluate position
            vPos_w = mathutils.Vector(xPolys.GetRandomPosOnPoly(iPlyIdx))
            # print(f"vPos_w: {vPos_w}")

            if bHasAngleConstraint is True or bUseCameraFov is True:
                vPos_cam = (matCamWorld_inv @ vPos_w.to_4d()).to_3d()
                vViewDir_cam = vPos_cam.normalized()
                vHorizPos_cam = matProjXZ @ vPos_cam
                vVertPos_cam = matProjYZ @ vPos_cam
                vHorizViewDir_cam = vHorizPos_cam.normalized()
                vVertViewDir_cam = vVertPos_cam.normalized()
                # print(vHorizViewDir_cam)
            # enddef

            bFovOK = True
            if bUseCameraFov is True:
                fCamDist = (vPos_w - vCamOrig).length
                lViewAngle_rad = [
                    abs(math.atan2(vHorizViewDir_cam.x, -vHorizViewDir_cam.z)),
                    abs(math.atan2(vVertViewDir_cam.y, -vVertViewDir_cam.z)),
                ]
                # lViewAngle_rad = [math.acos(abs(vHorizViewDir_cam.z)), math.acos(abs(vVertViewDir_cam.z))]
                bFovOK = (
                    lViewAngle_rad[0] <= lCamMaxViewAngle_rad[0]
                    and lViewAngle_rad[1] <= lCamMaxViewAngle_rad[1]
                    and fCamDist >= lCamDistRange[0]
                    and fCamDist <= lCamDistRange[1]
                )
            # endif

            # if no constraint is given, or this is the first point,
            # then accept the position
            # print("fMinDist: {}, len(lPnts): {}".format(fMinDist, len(lPnts)))
            if (
                bHasDistConstraint is False
                and bHasAngleConstraint is False
                and bUseCameraFov is False
                and bUseBoundBox is False
            ) or (bUseCameraFov is True and bFovOK is True and len(xObstacles) == 0 and len(dicPnts) == 0):
                break
            # endif

            bDistOK = True
            if bHasDistConstraint is True:
                lDist = [(vPos_w - x).length for i, x in dicPnts.items() if x is not None]
                # print("vPos: {}, lPnts: {}".format(vPos, lPnts))
                # print("MinDist: {}, lDist: {}".format(fMinDist, lDist))
                bDistOK = all(x >= fMinDist and x <= fMaxDist for x in lDist)
            # endif

            bAngleOK = True
            if bHasAngleConstraint is True:
                lAngle = [vHorizViewDir_cam.angle(x) for x in lHorizViewDir]
                bAngleOK = all(x >= fMinHorizViewAngleSep_rad for x in lAngle)
            # endif

            bBoundBoxOK = True
            if bUseBoundBox is True:
                # # !!! DEBUG
                # vPos_w = lBoxs[0]["vCtr"].copy()
                # vPos_w += mathutils.Vector((iTestPlyIdx*0.1, 0, 0))
                # print(f"vPos_w: {vPos_w}")
                # # !!!!!!!!!!!!!!!!!!!!!!
                xInst = xInstances[lInstNames[iPntIdx]]
                xBox = copy.deepcopy(xInst.xBoundBox)
                if lInstOrig is not None:
                    vNewCtr_w = vPos_w - xBox.GetDelta(lInstOrig)
                    vDelta = vNewCtr_w - xBox.vCenter
                elif sInstOrig == "ORIG":
                    vDelta = vPos_w - xInst.vOrigin
                else:
                    raise RuntimeError("Invalid instance origin")
                # endif

                xBox.Move(vDelta)

                for iIdx, xBoxX in dicBoxes.items():
                    # print("{}: Test -> {}, {}".format(iPntIdx, [x for x in dicBoxX["vCtr"]], dicBoxX["tSize"]))
                    if xBox.Intersects(xBoxX) is True:
                        bBoundBoxOK = False
                        break
                    # endif
                # endfor

                if bBoundBoxOK is True:
                    for xObst in xObstacles:
                        if xBox.Intersects(xObst.xBoundBox) is True:
                            bBoundBoxOK = False
                            break
                        # endif
                    # endfor
                # endif

                # print(f"bBoundBoxOK: {bBoundBoxOK}")
            # endif use bound box

            if bAngleOK is True and bDistOK is True and bFovOK is True and bBoundBoxOK is True:
                break
            # endif

            # Remove polynomial from polynomials to randomly choose from,
            # so that it is not selected again.
            lPlyIdx.remove(iPlyIdx)
            vPos_w = None
        # endwhile polynomials left

        if vPos_w is not None:
            dicPnts[iPntIdx] = vPos_w

            if bUseBoundBox is True:
                xInst = xInstances[lInstNames[iPntIdx]]
                xBox = copy.deepcopy(xInst.xBoundBox)
                if lInstOrig is not None:
                    vNewCtr_w = vPos_w - xBox.GetDelta(lInstOrig)
                    vDelta = vNewCtr_w - xBox.vCenter
                elif sInstOrig == "ORIG":
                    vDelta = vPos_w - xInst.vOrigin
                else:
                    raise RuntimeError("Invalid instance origin")
                # endif

                xBox.Move(vDelta)

                dicBoxes[iPntIdx] = xBox
            # endif

            if bHasAngleConstraint is True:
                lHorizViewDir.append(vHorizViewDir_cam)
                # print(lHorizViewDir)
            # endif
        else:
            dicPnts[iPntIdx] = None
        # endif
    # endfor point count

    # Transform to world coordinates
    # lPnts = [objX.matrix_world @ x for x in lPnts]

    if bUseBoundBox is True or bHasInst is True:
        dicTrgPnts = {}
        for iIdx, vPnt in dicPnts.items():
            if vPnt is None:
                dicTrgPnts[lInstNames[iIdx]] = None

            else:
                xInst = xInstances[lInstNames[iIdx]]
                xBB = xInst.xBoundBox

                if lInstOrig is not None:
                    vOrig = xBB.vCenter + xBB.GetDelta(lInstOrig)
                elif sInstOrig == "ORIG":
                    vOrig = xInst.vOrigin
                else:
                    raise RuntimeError("Invalid instance origin")
                # endif

                vTrgPnt = vPnt - vOrig
                # print(f"\ndicBB: {dicBB}")
                # print(f"vTrgPnt: {vTrgPnt}, vPnt: {vPnt}, vCtrBot: {vCtrBot}, location: {objA.location}")
                dicTrgPnts[lInstNames[iIdx]] = vTrgPnt
            # endif
        # endfor
        dicPnts = dicTrgPnts
    # endif

    return dicPnts


# enddef


######################################################
def GetRndPointsOnSurfaceUniformly(
    *,
    lTrgObjNames: list[str],
    iPntCnt: Optional[int] = None,
    fMinDist: float = 0.0,
    fMaxDist: float = math.inf,
    fMinHorizViewAngleSep_deg: float = 0.0,
    bUseCameraFov: bool = False,
    lCamFovBorder_deg: list[float] = [0.0, 0.0],
    lCamDistRange: list[float] = None,
    matCamWorld: Optional[mathutils.Matrix] = None,
    lCamFov_deg: Optional[list[float]] = None,
    lVexGrpNames: Optional[list[str]] = None,
    iSeed: Optional[int] = None,
    iMaxTrials: int = 20,
    xInstances: Optional[CInstances] = None,
    bUseBoundBox: bool = False,
    xInstanceOrigin: Union[list[float], str, None] = None,
    xObstacles: Optional[CInstances] = None,
) -> dict:
    """Create the given number of points at random positions on the surface.
       Takes into account the vertex weights of the given vertex group, if set.
       If instances are given to distribute on the surface, the delta to their
       current location is returned.

    Args:
        lTrgObjNames (str):
            A list of surface objects.

        iPntCnt (int):
            The number of points to generate

        fMinDist (float, optional):
            The minimal distance between points.
            If it is not possible to generate the given number of points
            due to this distance constraint, less points are returned.
            Defaults to 0.0.

        fMaxDist (float, optional):
            The maximal distance between points.
            If it is not possible to generate the given number of points
            due to this distance constraint, less points are returned.
            Defaults to math.inf.

        fMinHorizViewAngleSep_deg (float, optional, default=0.0):
            The minimal horizonal view angle separation in degrees of the generated points.
            The argumeent 'matCamWorld' must be specified.

        bUseCameraFov (bool, optional, default=false):
            Contraints points to the horizontal camera field of view if set to true.
            The arguments 'matCamWorld' and 'lCamFov_deg' must be specified.

        lCamFovBorder_deg (list[float], optional, default=[0.0, 0.0]):
            Only used when 'bUseCameraFov' is true.
            Specifies the horizontal and vertical FoV border around the actual camera FoV.

        lCamDistRange (list[float], optional, default=[0, inf]):
            Minimal and maximal distance from camera that are allowed.

        matCamWorld (mathutils.Matrix, optional, default=None):
            Only needed if 'fMinHorizViewAngleSep_deg' > 0 or 'bUseCameraFov' is true.
            Must be set to a 4x4 world matrix.

        lCamFov_deg (list[float], optional, default=None):
            Only needed 'bUseCameraFov' is true. Gives the camera's field of view.

        lVexGrpNames (list[str], optional):
            The name of the vertex group to use per element in lTrgObjNames.
            Points are distributed based on
            the "weight" defined for each vertex of this vertex group.
            In Blender use "Weight Paint" to draw these weights. Defaults to None.

        bUseBoundBox (bool, optional):
            If set to true, uses the bounding boxes of the objects passed in "lObjects"
            to determine their minimal distance. Defaults to false.

        xInstanceOrigin (list[float] or str, optional, default=[0,0,-0.5]):
            If it is a list it gives the origin of the instances' bounding box relative to their centers.
                For example, [0,0,-0.5] is the center of the bottom plane,
                and [0,0,0] is the center of the bounding box.
            If it is a string it can be one of the following:
                - "ORIG": uses the instance's origin for placement and not the bounding box

        xInstances (CInstances, optional):
            List of instances to distribute on surface. Must be given if "bUseBoundBox" is True.

        xObstacles (CInstances, optional):
            Only used when bUseBoundBox is true. Instances whose bounding boxes
            will not be intersected by the object's bounding boxes.

        iSeed (int, optional):
            The random seed to use. Defaults to None.

        iMaxTrials (int, optional):
            The maximal number of random trials to find a valid position
            for a point. Defaults to 20.

    Returns:
        list: A list of vectors of type mathutils.Vector, giving positions on the surface.
    """
    if iSeed is not None:
        random.seed(iSeed)
        np.random.seed(iSeed)
    # endif

    if fMaxDist is None:
        fMaxDist = math.inf
    # endif

    if iPntCnt is None and xInstances is None:
        raise RuntimeError("Neither point count nor list of objects is given")
    # endif

    if bUseBoundBox is True and xInstances is None:
        raise RuntimeError("If 'bUseBoundBox' is true, need to specify list of objects")
    # endif

    if lCamDistRange is None:
        lCamDistRange = [0.0, math.inf]
    # endif

    if isinstance(xInstances, CInstances):
        bHasInst = True
        lInstNames = xInstances.lNames
    else:
        bHasInst = False
        lInstNames = None
    # endif

    if iPntCnt is None:
        iPntCnt = len(xInstances)
    # endif

    sInstOrig = None
    lInstOrig = None
    if isinstance(xInstanceOrigin, str):
        sInstOrig = xInstanceOrigin
        if sInstOrig not in ["ORIG"]:
            raise RuntimeError(f"Instance origin string must be 'ORIG', but '{sInstOrig}' was given")
        # endif
    elif isinstance(xInstanceOrigin, list):
        lInstOrig = xInstanceOrigin
        if len(lInstOrig) != 3:
            raise RuntimeError("Instance origin list must be of length three")
        # endif
    else:
        raise RuntimeError(f"Invalid instance origin argument: {xInstanceOrigin}")
    # endif

    lMatrixWorld = []
    xPolys = CPolygons()

    for iIdx, sTrgObjName in enumerate(lTrgObjNames):
        sVexGrpName = None
        if isinstance(lVexGrpNames, list) and iIdx < len(lVexGrpNames) and isinstance(lVexGrpNames[iIdx], str):
            sVexGrpName = lVexGrpNames[iIdx]
        # endif
        xPolys.AddFromObject(_sObjectName=sTrgObjName, _sVexGrpName=sVexGrpName)
        lMatrixWorld.append(bpy.data.objects[sTrgObjName].matrix_world)
    # endfor

    bHasDistConstraint = fMinDist > 1e-7 or fMaxDist != math.inf
    bHasAngleConstraint = fMinHorizViewAngleSep_deg > 1e-6

    # If a minimal view angle is specified, get the active camera
    fMinHorizViewAngleSep_rad = None
    # fCamHorizFov_rad = None
    if bHasAngleConstraint is True or bUseCameraFov is True:
        if matCamWorld is None:
            raise RuntimeError("No camera world matrix given")
        # endif

        if bUseCameraFov is True and lCamFov_deg is None:
            raise RuntimeError("No horizontal camera field of view given")
        else:
            if abs(lCamFov_deg[0]) / 2.0 - lCamFovBorder_deg[0] <= 0.1:
                raise RuntimeError("Horizontal camera FoV border is too large")
            # endif
            if abs(lCamFov_deg[1]) / 2.0 - lCamFovBorder_deg[1] <= 0.1:
                raise RuntimeError("Vertical camera FoV border is too large")
            # endif
            lCamFov_rad = [math.radians(abs(x)) for x in lCamFov_deg]
            lCamMaxViewAngle_rad = [lCamFov_rad[i] / 2.0 - math.radians(lCamFovBorder_deg[i]) for i in range(2)]
        # endif

        fMinHorizViewAngleSep_rad = math.radians(abs(fMinHorizViewAngleSep_deg))
        matProjXZ = mathutils.Matrix.OrthoProjection("XZ", 3)
        matProjYZ = mathutils.Matrix.OrthoProjection("YZ", 3)
        matCamWorld_inv = matCamWorld.inverted()
        vCamOrig = matCamWorld.to_translation().to_3d()
    # endif

    # print(iPlyCnt)
    iPlyCnt = xPolys.iTotalPolyCount
    # print(iPlyCnt)

    dicPnts: dict[int, mathutils.Vector] = {}
    dicBoxes: dict[int, CBoundingBox] = {}
    lHorizViewDir = []
    vHorizViewDir_cam = None
    lPlyIdx: list[int] = list(range(0, iPlyCnt))

    for iPntIdx in range(0, iPntCnt):
        # print(f"Test point {iPntIdx}")
        vPos_w = None

        # Try to find a position as long as there are polynomials
        # to chose from
        iAttempt = 0
        while iAttempt < iMaxTrials:
            # Evaluate position
            vPos_w = mathutils.Vector(xPolys.SampleUniformlyByWeightAndArea())
            # print(f"vPos_w: {vPos_w}")

            if bHasAngleConstraint is True or bUseCameraFov is True:
                vPos_cam = (matCamWorld_inv @ vPos_w.to_4d()).to_3d()
                vViewDir_cam = vPos_cam.normalized()
                vHorizPos_cam = matProjXZ @ vPos_cam
                vVertPos_cam = matProjYZ @ vPos_cam
                vHorizViewDir_cam = vHorizPos_cam.normalized()
                vVertViewDir_cam = vVertPos_cam.normalized()
                # print(vHorizViewDir_cam)
            # enddef

            bFovOK = True
            if bUseCameraFov is True:
                fCamDist = (vPos_w - vCamOrig).length
                lViewAngle_rad = [
                    abs(math.atan2(vHorizViewDir_cam.x, -vHorizViewDir_cam.z)),
                    abs(math.atan2(vVertViewDir_cam.y, -vVertViewDir_cam.z)),
                ]
                bFovOK = (
                    lViewAngle_rad[0] <= lCamMaxViewAngle_rad[0]
                    and lViewAngle_rad[1] <= lCamMaxViewAngle_rad[1]
                    and fCamDist >= lCamDistRange[0]
                    and fCamDist <= lCamDistRange[1]
                )
            # endif

            # if no constraint is given, or this is the first point,
            # then accept the position
            # print("fMinDist: {}, len(lPnts): {}".format(fMinDist, len(lPnts)))
            if (
                bHasDistConstraint is False
                and bHasAngleConstraint is False
                and bUseCameraFov is False
                and bUseBoundBox is False
            ) or (bUseCameraFov is True and bFovOK is True and len(xObstacles) == 0 and len(dicPnts) == 0):
                break
            # endif

            bDistOK = True
            if bHasDistConstraint is True:
                lDist = [(vPos_w - x).length for i, x in dicPnts.items() if x is not None]
                # print("vPos: {}, lPnts: {}".format(vPos, lPnts))
                # print("MinDist: {}, lDist: {}".format(fMinDist, lDist))
                bDistOK = all(x >= fMinDist and x <= fMaxDist for x in lDist)
            # endif

            bAngleOK = True
            if bHasAngleConstraint is True:
                lAngle = [vHorizViewDir_cam.angle(x) for x in lHorizViewDir]
                bAngleOK = all(x >= fMinHorizViewAngleSep_rad for x in lAngle)
            # endif

            bBoundBoxOK = True
            if bUseBoundBox is True:
                # # !!! DEBUG
                # vPos_w = lBoxs[0]["vCtr"].copy()
                # vPos_w += mathutils.Vector((iTestPlyIdx*0.1, 0, 0))
                # print(f"vPos_w: {vPos_w}")
                # # !!!!!!!!!!!!!!!!!!!!!!
                xInst = xInstances[lInstNames[iPntIdx]]
                xBox = copy.deepcopy(xInst.xBoundBox)
                if lInstOrig is not None:
                    vNewCtr_w = vPos_w - xBox.GetDelta(lInstOrig)
                    vDelta = vNewCtr_w - xBox.vCenter
                elif sInstOrig == "ORIG":
                    vDelta = vPos_w - xInst.vOrigin
                else:
                    raise RuntimeError("Invalid instance origin")
                # endif

                xBox.Move(vDelta)

                for iIdx, xBoxX in dicBoxes.items():
                    # print("{}: Test -> {}, {}".format(iPntIdx, [x for x in dicBoxX["vCtr"]], dicBoxX["tSize"]))
                    if xBox.Intersects(xBoxX) is True:
                        bBoundBoxOK = False
                        break
                    # endif
                # endfor

                if bBoundBoxOK is True:
                    for xObst in xObstacles:
                        if xBox.Intersects(xObst.xBoundBox) is True:
                            bBoundBoxOK = False
                            break
                        # endif
                    # endfor
                # endif

                # print(f"bBoundBoxOK: {bBoundBoxOK}")
            # endif use bound box

            if bAngleOK is True and bDistOK is True and bFovOK is True and bBoundBoxOK is True:
                break
            # endif

            # Remove polynomial from polynomials to randomly choose from,
            # so that it is not selected again.
            iAttempt += 1
            vPos_w = None
        # endwhile polynomials left

        if vPos_w is not None:
            dicPnts[iPntIdx] = vPos_w

            if bUseBoundBox is True:
                xInst = xInstances[lInstNames[iPntIdx]]
                xBox = copy.deepcopy(xInst.xBoundBox)
                if lInstOrig is not None:
                    vNewCtr_w = vPos_w - xBox.GetDelta(lInstOrig)
                    vDelta = vNewCtr_w - xBox.vCenter
                elif sInstOrig == "ORIG":
                    vDelta = vPos_w - xInst.vOrigin
                else:
                    raise RuntimeError("Invalid instance origin")
                # endif

                xBox.Move(vDelta)

                dicBoxes[iPntIdx] = xBox
            # endif

            if bHasAngleConstraint is True:
                lHorizViewDir.append(vHorizViewDir_cam)
                # print(lHorizViewDir)
            # endif
        else:
            dicPnts[iPntIdx] = None
        # endif
    # endfor point count

    # Transform to world coordinates
    # lPnts = [objX.matrix_world @ x for x in lPnts]

    if bUseBoundBox is True or bHasInst is True:
        dicTrgPnts = {}
        for iIdx, vPnt in dicPnts.items():
            if vPnt is None:
                dicTrgPnts[lInstNames[iIdx]] = None

            else:
                xInst = xInstances[lInstNames[iIdx]]
                xBB = xInst.xBoundBox

                if lInstOrig is not None:
                    vOrig = xBB.vCenter + xBB.GetDelta(lInstOrig)
                elif sInstOrig == "ORIG":
                    vOrig = xInst.vOrigin
                else:
                    raise RuntimeError("Invalid instance origin")
                # endif

                vTrgPnt = vPnt - vOrig
                # print(f"\ndicBB: {dicBB}")
                # print(f"vTrgPnt: {vTrgPnt}, vPnt: {vPnt}, vCtrBot: {vCtrBot}, location: {objA.location}")
                dicTrgPnts[lInstNames[iIdx]] = vTrgPnt
            # endif
        # endfor
        dicPnts = dicTrgPnts
    # endif

    return dicPnts


# enddef
