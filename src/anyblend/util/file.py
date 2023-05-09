#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \modules\anyblend\util\file.py
# Created Date: Tuesday, February 16th 2021, 9:41:52 am
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

import pyjson5
import json


#######################################################################
# Load JSON file from path
def LoadJson(_sFilePath):

    with open(_sFilePath, "r") as xFile:
        dicData = pyjson5.decode_io(xFile)
    # endwith

    return dicData


# enddef


#######################################################################
# save JSON file from relative path to script path
def SaveJson(_sFilePath, _dicData, iIndent=-1):

    with open(_sFilePath, "w") as xFile:
        if iIndent < 0 or _sFilePath.endswith(".json5"):
            pyjson5.encode_io(_dicData, xFile, supply_bytes=False)
        else:
            json.dump(_dicData, xFile, indent=iIndent)
        # endif
    # endwith


# enddef
