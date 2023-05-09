#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /util.py
# Created Date: Thursday, October 22nd 2020, 1:20:20 pm
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

from anybase.cls_any_error import CAnyError_Message

dicHandler = {}


#####################################################################################
def GetAnimHandlerDict():
    global dicHandler
    return dicHandler


# enddef


#####################################################################################
def RegisterAnimHandler(_sId, _dicH):

    global dicHandler

    if _dicH is None:
        raise Exception("No handler data given")
    # endif

    try:
        funcHandler = _dicH.get("handler")
        if funcHandler is None:
            raise Exception("No function handler given for id '{0}'.".format(_sId))
        # endif

        # remove any previous handler with same id
        # RemoveAnimHandler(_sId)

        dicHandler[_sId] = _dicH
        bpy.app.handlers.frame_change_pre.append(funcHandler)

        # Execute handler for current frame
        funcHandler(bpy.context.scene, None)
    except Exception as xEx:
        raise CAnyError_Message(sMsg=f"Error registering animation handler '{_sId}'", xChildEx=xEx)
    # endtry

# enddef


#####################################################################################
def RemoveAnimHandler(_sId):

    global dicHandler
    dicH = dicHandler.get(_sId)

    if dicH is None:
        return
    # endif

    # print(f"Removing animation handler for '{_sId}'")

    try:
        funcHandler = dicH.get("handler")
        if funcHandler is not None:
            # print(f"{funcHandler}")
            bpy.app.handlers.frame_change_pre.remove(funcHandler)
        # endif

        funcFinalizer = dicH.get("finalizer")
        if funcFinalizer is not None:
            funcFinalizer()
        # endif

        del dicHandler[_sId]
    except Exception as xEx:
        print(f"> ERROR removing animation handler: {(str(xEx))}")
    # endtry


# enddef


#####################################################################################
def ClearAnim():
    global dicHandler

    for sId in list(dicHandler.keys()):
        RemoveAnimHandler(sId)
    # endfor

    dicHandler = {}


# enddef


#####################################################################################
def RegisterAnimObject(_sObj, _dicAnim, _funcFactory):

    sAnimType = _dicAnim.get("sDTI", _dicAnim.get("sType"))
    sHandlerId = "{0}/{1}".format(_sObj, sAnimType)

    RegisterAnimHandler(sHandlerId, _funcFactory(_sObj, _dicAnim))


# enddef


#####################################################################################
# removes all anim handlers of object if no dicAnim is given.
# Otherwise, only the animation of the type specified in _dicAnim is removed.
def RemoveAnimObject(_sObj, dicAnim=None):

    global dicHandler

    if dicAnim is None:
        for sId in list(dicHandler.keys()):
            if sId.startswith(_sObj):
                RemoveAnimHandler(sId)
            # endif
        # endfor
    else:
        sAnimType = dicAnim.get("sDTI", dicAnim.get("sType"))
        sHandlerId = "{0}/{1}".format(_sObj, sAnimType)
        RemoveAnimHandler(sHandlerId)
    # endif


# enddef
