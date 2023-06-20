#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \object_ops.py
# Created Date: Monday, June 19th 2023
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


###################################################################
def _TempContextForImage(_imgX: bpy.types.Image) -> bpy.types.Context:
    xCtx = bpy.context.copy()
    xCtx["edit_image"] = _imgX

    return bpy.context.temp_override(**xCtx)


# enddef


###################################################################
def Pack(_imgX: bpy.types.Image):
    _imgX.use_fake_user = True
    with _TempContextForImage(_imgX):
        bpy.ops.image.pack()
    # endwith


# enddef
