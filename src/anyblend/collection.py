#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \blend\collection.py
# Created Date: Thursday, April 29th 2021, 2:20:21 pm
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
from typing import Union


#################################################################
def GetActiveLayerCollection(_xContext):
    return _xContext.view_layer.active_layer_collection


# enddef


#################################################################
def GetActiveCollection(_xContext: bpy.types.Context) -> bpy.types.Collection:
    return GetActiveLayerCollection(_xContext).collection


# enddef


#################################################################
def SetActiveLayerCollection(_xContext, _xLayCol):
    _xContext.view_layer.active_layer_collection = _xLayCol


# enddef


#################################################################
def MakeRootLayerCollectionActive(_xContext):
    _xContext.view_layer.active_layer_collection = _xContext.view_layer.layer_collection


# enddef


#################################################################
def GetRootLayerCollection(_xContext):
    return _xContext.view_layer.layer_collection


# enddef


#################################################################
def GetRootCollection(_xContext):
    return _xContext.view_layer.layer_collection.collection


# enddef


#################################################################
def GetCollection(_sName: str, bDoThrow: bool = False) -> bpy.types.Collection:
    clnAct = bpy.data.collections.get(_sName)
    if clnAct is None and bDoThrow:
        raise RuntimeError("Collection '{}' not found".format(_sName))
    # endif

    return clnAct


# enddef


#################################################################
def _DoGetParentCollection(_clnStart, _clnX):
    if _clnX.name in _clnStart.children:
        return _clnStart
    # endif

    if len(_clnStart.children) == 0:
        return None
    # endif

    for clnChild in _clnStart.children:
        clnParent = _DoGetParentCollection(clnChild, _clnX)
        if clnParent is not None:
            return clnParent
        # endif
    # endfor

    return None


# enddef


#################################################################
def GetParentCollection(_clnX, *, _xContext=None):
    if _xContext is None:
        _xContext = bpy.context
    # endif

    clnRoot = GetRootCollection(_xContext)
    return _DoGetParentCollection(clnRoot, _clnX)


# enddef


# ###################################################################################
def GetCollectionObjects(
    _clnX, *, _bChildren: bool = False, _bRecursive: bool = False, _lObjectTypes: list[str] = None
) -> list[str]:
    """Get objects of collection _clnX.

    Parameters
    ----------
    _clnX : Blender collection
        The Blender collection from which the objects are collected.
    _bChildren : bool, optional
        If False, only objects that have no parent in collection _clnX are selected, by default False
    _bRecursive : bool, optional
        If True, iterates through child collections, by default False

    Returns
    -------
    list
        List of objects found.
    """

    if _bChildren is False:
        lObjects = [
            x.name
            for x in _clnX.objects
            if (x.parent is None or (x.parent is not None and x.parent.name not in _clnX.objects))
            and (_lObjectTypes is None or x.type in _lObjectTypes)
        ]
    else:
        lObjects = [x.name for x in _clnX.objects if _lObjectTypes is None or x.type in _lObjectTypes]
    # endif

    if _bRecursive is True:
        for clnChild in _clnX.children:
            lChildObjects = GetCollectionObjects(
                clnChild, _bChildren=_bChildren, _bRecursive=True, _lObjectTypes=_lObjectTypes
            )
            lObjects.extend(lChildObjects)
        # endfor
    # endif

    return lObjects


# enddef


#################################################################
def FindObjectInCollection(_clX, _objX):
    if _objX.name in _clX.objects:
        return _clX, _objX
    # endif

    for clChild in _clX.children:
        clX, objX = FindObjectInCollection(clChild, _objX)
        if objX is not None:
            return clX, objX
        # endif
    # endfor

    return None, None


# enddef


#################################################################
def FindCollectionOfObject(_xContext, _objX):
    clRoot = GetRootLayerCollection(_xContext).collection
    clX, objX = FindObjectInCollection(clRoot, _objX)

    return clX


# enddef


#################################################################
def _DoFindParentCollectionOfCollection(_clnParent, _clnChild):
    if _clnChild.name in _clnParent.children:
        return _clnParent, _clnChild
    # endif

    for clnChild in _clnParent.children:
        clnParent, clnTheChild = _DoFindParentCollectionOfCollection(clnChild, _clnChild)
        if clnTheChild is not None:
            return clnParent, clnTheChild
        # endif
    # endfor

    return None, None


# enddef


#################################################################
def FindParentCollectionOfCollection(_xContext, _clnChild) -> bpy.types.Collection:
    clnRoot = GetRootLayerCollection(_xContext).collection
    clnParent, clnChild = _DoFindParentCollectionOfCollection(clnRoot, _clnChild)

    return clnParent


# enddef


#################################################################
def FindLayerCollection(_xLayCol, _sName):
    # print(f"Find layer collection {_xLayCol.name} ?= {_sName}")
    if _xLayCol.name == _sName:
        return _xLayCol
    # endif

    # DEBUG #
    # lChildren = [x.name for x in _xLayCol.children]
    # print(f"Children: {lChildren}")
    #########

    xLC = _xLayCol.children.get(_sName)
    if xLC is None:
        for xChild in _xLayCol.children:
            xLC = FindLayerCollection(xChild, _sName)
            if xLC is not None:
                break
            # endif
        # endfor
    # endif

    return xLC


# enddef


#################################################################
def SetActiveCollection(_xContext, _sName):
    xLC = FindLayerCollection(_xContext.view_layer.layer_collection, _sName)
    if xLC is not None:
        _xContext.view_layer.active_layer_collection = xLC
    else:
        raise Exception("Layer collection '{0}' not found.".format(_sName))
    # endif


# enddef


#################################################################
def IsExcluded(_xContext, _sName):
    xLC = FindLayerCollection(_xContext.view_layer.layer_collection, _sName)
    return xLC.exclude


# enddef


#################################################################
def ExcludeCollection(_xContext, _sName, _bExclude=True):
    xLC = FindLayerCollection(_xContext.view_layer.layer_collection, _sName)
    if xLC is not None:
        xLC.exclude = _bExclude
    else:
        raise Exception("Layer collection '{0}' not found.".format(_sName))
    # endif


# enddef


#################################################################
def ProvideCollection(_xContext, _sName, bActivate=True, clnParent=None, bEnsureLayerCollectionExists=False):
    # There was a case, where the collection already existed but without
    # an associated layer collection. In this case, we need to delete the
    # collection and re-create it.
    clX = GetCollection(_sName)

    if bEnsureLayerCollectionExists is True:
        clLayX = FindLayerCollection(_xContext.view_layer.layer_collection, _sName)

        if clX is None or clLayX is None:
            if clX is not None:
                bpy.data.collections.remove(clX)
            # endif
            clX = CreateCollection(bpy.context, _sName, bActivate=bActivate, clnParent=clnParent)
        # endif
    else:
        if clX is None:
            clX = CreateCollection(bpy.context, _sName, bActivate=bActivate, clnParent=clnParent)
        # endif
    # endif

    return clX


# enddef


#################################################################
def CreateCollection(_xContext, _sName, bActivate=True, clnParent=None):
    if clnParent is None:
        xColAct = GetActiveCollection(_xContext)
    else:
        xColAct = clnParent
    # endif

    xCollection = bpy.data.collections.new(_sName)
    xColAct.children.link(xCollection)

    if bActivate:
        SetActiveCollection(_xContext, xCollection.name)
    # endif

    return xCollection


# enddef


#################################################################
def CreateCollectionHierarchy(
    _xContext: bpy.types.Context, _lClnHierarchy: list[str], bActivate: bool = True, bCreateHierarchyNames: bool = True
) -> bpy.types.Collection:
    if not isinstance(_lClnHierarchy, list):
        raise Exception("Collection hierarchy must be a list of string")
    # endif

    if len(_lClnHierarchy) == 0:
        return
    # endif

    # Make the root layer collection active, so that CreateCollection() creates
    # layer collection in root layer collection.
    MakeRootLayerCollectionActive(_xContext)

    # Get container of collections
    xClns = bpy.data.collections

    sTopClnName = _lClnHierarchy[0]
    if sTopClnName not in xClns:
        # Create the collection and make it child of active collection
        # Also makes the created collection active
        clnTop = CreateCollection(_xContext, sTopClnName)
    else:
        clnTop = xClns[sTopClnName]
        SetActiveCollection(_xContext, sTopClnName)
    # endif

    # Create the remaining hierarchy
    clnAct = clnTop
    sFullClnName = sTopClnName

    for sClnName in _lClnHierarchy[1:]:
        sFullClnName += "." + sClnName
        if bCreateHierarchyNames:
            sNewClnName = sFullClnName
        else:
            sNewClnName = sClnName
        # endif

        if sNewClnName not in xClns:
            clnAct = CreateCollection(_xContext, sNewClnName)

        else:
            # Test whether a collection already exists but is not a child
            # of the hierarchy level above it.
            if sNewClnName not in clnAct.children:
                raise Exception(
                    "Collection '{0}' already exists outside the given hierarchy: {1}".format(
                        sNewClnName, "/".join(_lClnHierarchy)
                    )
                )
            # endif

            # Collection exists and is child of currently active collection
            clnAct = xClns[sNewClnName]
            SetActiveCollection(_xContext, sNewClnName)

        # endif
    # endfor hierarchy

    return clnAct


# enddef


#################################################################
def MoveObjectToActiveCollection(_xContext, _objX, bMoveObjectHierarchy=True):
    clnAct = GetActiveCollection(_xContext)
    clnObj = FindCollectionOfObject(_xContext, _objX)

    if clnObj is not None:
        clnObj.objects.unlink(_objX)
    # endif
    clnAct.objects.link(_objX)

    if bMoveObjectHierarchy is True:
        for objChild in _objX.children:
            # Find collection child object is in.
            # This is not necessarily the same collection as the object's.
            clnX = FindCollectionOfObject(_xContext, objChild)
            if clnX is not None:
                clnX.objects.unlink(objChild)
            # endif
            clnAct.objects.link(objChild)
        # endfor
    # endif


# enddef


#################################################################
def AddObjectToCollectionHierarchy(
    _xContext,
    _objX,
    _lCollectionHierarchy,
    bCreateHierarchyNames=True,
    bMoveObjectHierarchy=True,
):
    """Generates hierarchy of collections from lCollectionHierarchy if not
    already existing. Unlinks object from collection it is in and links it to last level of hierarchy

    Args:
        _xContext (bpy.types.Context): The Blender context
        _objX (bpy.types.Object): The object to place in the collection
        _lCollectionHierarchy (list): list of strings of collection hierarchy
        bCreateHierarchyNames (bool): If true, the given hierarchy names are concatenated with dots
        bMoveObjectHierarchy (bool): If true, the objects and its' children are removed from their current
                                     collection and placed in the new collection.

    Raises:
        Exception: If a child element in the given collection hierarchy already exists in a different hierarchy.
    """

    CreateCollectionHierarchy(
        _xContext,
        _lCollectionHierarchy,
        bActivate=True,
        bCreateHierarchyNames=bCreateHierarchyNames,
    )

    MoveObjectToActiveCollection(_xContext, _objX, bMoveObjectHierarchy=bMoveObjectHierarchy)


# enddef


#################################################################
def _RemoveCollection(xColl, bRecursive=True, bRemoveObjects=True):
    # print(f"> Cln: {xColl.name}")
    if bRemoveObjects:
        lObj = [x for x in xColl.objects if x.users <= 1]
        for xObj in lObj:
            # print(f"> > Obj: {xObj.name}")
            bpy.data.objects.remove(xObj)
        # endfor
        del lObj
    # endif

    if bRecursive:
        for xChild in xColl.children:
            _RemoveCollection(xChild, bRecursive=True, bRemoveObjects=bRemoveObjects)
        # endfor
    # endif

    bpy.data.collections.remove(xColl)


# enddef


#################################################################
def RemoveCollection(
    _xCln: Union[str, bpy.types.Collection],
    bRecursive: bool = True,
    bRemoveObjects: bool = True,
    bRemoveOrphaned: bool = True,
    bIgnoreFakeUser: bool = False,
):
    xColl: bpy.types.Collection = None

    if isinstance(_xCln, str):
        xColl = bpy.data.collections.get(_xCln)
        if xColl is None:
            raise Exception("Collection '{0}' not found.".format(_xCln))
        # endif
    elif isinstance(_xCln, bpy.types.Collection):
        xColl = _xCln
    else:
        raise RuntimeError("Collection argument has invalid type")
    # endif

    if bRemoveOrphaned:
        lExclude = FindOrphaned()
    # endif

    _RemoveCollection(xColl, bRecursive=bRecursive, bRemoveObjects=bRemoveObjects)

    if bRemoveOrphaned:
        RemoveOrphaned(lExclude=lExclude, bIgnoreFakeUser=bIgnoreFakeUser)
    # endif


# enddef


#################################################################
def _RemoveCollectionObjects(xColl, bRecursive=True):
    lObj = [x for x in xColl.objects if x.users <= 1]
    for xObj in lObj:
        bpy.data.objects.remove(xObj)
    # endfor
    del lObj

    if bRecursive:
        for xChild in xColl.children:
            _RemoveCollectionObjects(xChild, bRecursive=True)
        # endfor
    # endif


# enddef


#################################################################
def RemoveCollectionObjects(_sName, bRecursive=True, bRemoveOrphaned=True, bIgnoreFakeUser=False):
    xColl = bpy.data.collections.get(_sName)
    if xColl is None:
        raise Exception("Collection '{0}' not found.".format(_sName))
    # endif

    if bRemoveOrphaned:
        lExclude = FindOrphaned()
    # endif

    _RemoveCollectionObjects(xColl, bRecursive=bRecursive)

    if bRemoveOrphaned:
        RemoveOrphaned(lExclude=lExclude, bIgnoreFakeUser=bIgnoreFakeUser)
    # endif


# enddef


#################################################################
def FindOrphaned(lExclude=None, bIgnoreFakeUser=False):
    lData = [
        bpy.data.objects,
        bpy.data.meshes,
        bpy.data.particles,
        bpy.data.materials,
        bpy.data.textures,
        bpy.data.images,
    ]

    lOrphanList = []

    # Loop over data sets
    for iIdx, xData in enumerate(lData):
        # Find orphaned elements
        if bIgnoreFakeUser:
            lOrphan = [x for x in xData if x.users == 0 or (x.use_fake_user and x.users == 1)]
        else:
            lOrphan = [x for x in xData if x.users == 0]
        # endif

        if lExclude is not None:
            lEx = lExclude[iIdx].get("lOrphan")
            lOrphan = [x for x in lOrphan if x not in lEx]
        # endif

        lOrphanList.append({"xSrc": lData[iIdx], "lOrphan": lOrphan})
    # endfor

    return lOrphanList


# enddef


#################################################################
def RemoveOrphaned(lExclude=None, bIgnoreFakeUser=False):
    # Loop over all given data sets until no more orphans are found
    while True:
        bHasOrphans = False

        lOrphanList = FindOrphaned(lExclude=lExclude, bIgnoreFakeUser=bIgnoreFakeUser)

        # Loop over data sets
        for dicOrphan in lOrphanList:
            xSrc = dicOrphan.get("xSrc")
            lOrphan = dicOrphan.get("lOrphan")

            if len(lOrphan) > 0:
                bHasOrphans = True
            # endif

            # Remove all orphaned elements
            for xEl in lOrphan:
                xSrc.remove(xEl)
            # endfor
        # endfor

        if not bHasOrphans:
            break
        # endif
    # endwhile


# enddef
