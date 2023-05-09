#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /prefs.py
# Created Date: Thursday, October 22nd 2020, 1:20:25 pm
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

import os
import bpy

from anybase.cls_any_error import CAnyError_Message


def UseComputeDevices(
    *,
    xContext=None,
    bSaveUserPrefs: bool = False,
    sComputeDeviceType: str = "CUDA",
    bCombinedCpuCompute: bool = False,
    bPrintInfo: bool = False,
):

    # Get the Blender version
    lVersion = bpy.app.version

    # # Get list of selected CUDA devices from environment variable
    # try:
    #     lSelDevIndices = [int(x) for x in os.environ['CUDA_VISIBLE_DEVICES'].split(', ')]
    # except Exception:
    #     lSelDevIndices = [0]
    # # endtry

    # print()
    # print("Selected CUDA devices: ")
    # print(lSelDevIndices)

    # For Blender 2.8 and for 2.79
    if lVersion[0] > 2 or (lVersion[0] == 2 and lVersion[1] >= 80):
        # print("Using Blender 2.8x settings!")
        # Get cycles preferences
        prefs = xContext.preferences.addons["cycles"].preferences
    else:
        # print("Using Blender 2.7x settings!")
        # Get cycles preferences
        prefs = xContext.user_preferences.addons["cycles"].preferences
    # endif

    if sComputeDeviceType == "NONE":
        sComputeDeviceType = "CPU"
    # endif

    # Set the compute type to CUDA
    if sComputeDeviceType == "CPU":
        prefs.compute_device_type = "NONE"
    else:
        try:
            prefs.compute_device_type = sComputeDeviceType
        except Exception as xEx:
            raise CAnyError_Message(
                f"Compute device type '{sComputeDeviceType}' not available",
                xChildEx=xEx,
            )
        # endtry
    # endif

    if bPrintInfo is True:
        print("")
        print("Compute Device Type: " + prefs.compute_device_type)
    # endif

    # Reset the device list...
    prefs.devices.clear()
    # ...and load it again.
    prefs.get_devices()

    # Enable only those devices for rendering that are selected
    lCudaDevices = []
    for xDev in prefs.devices:
        if bPrintInfo is True:
            print("==========================================")
            print("Device: " + xDev.name)
            print("Type: " + xDev.type)
        # endif

        if xDev.type == sComputeDeviceType or (
            xDev.type == "CPU" and bCombinedCpuCompute is True
        ):
            # Only the devices set visible by CUDA_VISIBLE_DEVICES are actually visible
            xDev.use = True
            # xDev.use = (iDeviceIdx in lSelDevIndices)
            lCudaDevices.append(xDev)

        else:
            xDev.use = False
        # endif

        if bPrintInfo is True:
            print("Use: " + ("true" if xDev.use else "false"))
            print("")
        # endif
    # endfor

    # print("Save user preferences.")
    if bSaveUserPrefs:
        bpy.ops.wm.save_userpref()
    # endif

    return lCudaDevices


# enddef


def PrintUsedDevices(_lDevices):

    for xDev in _lDevices:
        if xDev.use:
            print(xDev.name, flush=True)
        # endif
    # endfor


# enddef
