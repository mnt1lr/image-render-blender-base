#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \blend\viewlayer.py
# Created Date: Thursday, April 29th 2021, 3:59:34 pm
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

######################################################################################
# The only way I found on how to force an update of drivers
# is to change the current scene frame.
# So, here we are changing the frame by one and then back again.


def UpdateDrivers(*, _xScene=None):

    if _xScene is None:
        xScene = bpy.context.scene

    else:
        xScene = _xScene
    # endif

    iFrameIdx = xScene.frame_current
    xScene.frame_set(iFrameIdx + 1)
    xScene.frame_set(iFrameIdx)


# enddef
