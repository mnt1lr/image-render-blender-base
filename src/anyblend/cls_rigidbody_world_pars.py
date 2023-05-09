#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_rigidbody_world_pars.py
# Created Date: Friday, November 11th 2022, 8:29:45 am
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


class CRigidBodyWorldPars:
    def __init__(self, *, _scnX=None):
        self.fTimeScale: float = 1.0
        self.iSubStepsPerFrame: int = 10
        self.iSolverIterations: int = 10
        self.iFrameStart: int = 1
        self.iFrameEnd: int = 250

        if _scnX is not None and _scnX.rigidbody_world is not None:
            self.InitFromScene(_scnX)
        # endif

    # enddef

    def InitFromScene(self, _scnX):
        xRBW = _scnX.rigidbody_world
        if xRBW is None:
            raise RuntimeError("Scene has no rigid body world")
        # endif

        self.fTimeScale = xRBW.time_scale
        self.iSubStepsPerFrame = xRBW.substeps_per_frame
        self.iSolverIterations = xRBW.solver_iterations
        self.iFrameStart = xRBW.point_cache.frame_start
        self.iFrameEnd = xRBW.point_cache.frame_end

    # enddef

    def ApplyToScene(self, _scnX):
        xRBW = _scnX.rigidbody_world
        if xRBW is None:
            raise RuntimeError("Scene has no rigid body world")
        # endif

        xRBW.time_scale = self.fTimeScale
        xRBW.substeps_per_frame = self.iSubStepsPerFrame
        xRBW.solver_iterations = self.iSolverIterations
        xRBW.point_cache.frame_start = self.iFrameStart
        xRBW.point_cache.frame_end = self.iFrameEnd

    # enddef


# endclass
