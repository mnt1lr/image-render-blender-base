#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \modules\anyblend\util\modules.py
# Created Date: Tuesday, February 16th 2021, 9:43:26 am
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

import sys

###############################################################################
# Unload all anycam modules
def UnloadModules():
    # Unload anycam modules when the addon is unregistered to enable debugging.
    lUnloadMods = []
    for sModName in sys.modules:
        #    print(sModName)
        if "anyblend" in sModName or "AnyBlend" in sModName:
            lUnloadMods.append(sModName)
        # endif
    # endfor

    for sModName in lUnloadMods:
        # print("Unloading: " + sModName)
        del sys.modules[sModName]
    # endfor


# enddef
