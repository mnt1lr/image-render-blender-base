#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \asset_placement.py
# Created Date: Thursday, September 1st 2022, 4:43:48 pm
# Created by: Jochen Kall
# <LICENSE id="All-Rights-Reserved">
# Copyright (c) 2022 Robert Bosch GmbH and its subsidiaries
# </LICENSE>
###

# This module provides functions to compute asset placement maps using raycasting.
# Functionality includes generation of geometric placement maps, i.e. producing
# a map on a grid indicating whether an asset of a certain size could be placed at that position
# and generation of visibility maps, i.e. generating a map conveying the information whether
# an asset placed at that position would be visible on a specific camera

# Example usage
# import anyblend.asset_placement as ap
# Create geometric placement map for a single asset plane with asset radius 40 and asset height 180
# ap.GeneratePlacementMap(bpy.data.objects["Person.Plane"],fR=40,fH=180)
# Create visibility maps for all Anycam camsets and a collection of ASset planes, w.r.t a collection of walls
# ap.GenerateAnycamVisibilityMaps(bpy.data.collections["Assetplanes"],bpy.data.collections["Walls"],fR=40,fFov=180)
import bpy
import numpy as np
import mathutils

from anyblend.util.convert import BlenderUnitsPerMeterFactor


def BlenderVerts2np(objBlenderobject):
    """Efficient extraction of Vertex positions to a Numpy array

    Parameters
    ----------
    objBlenderobject : Blender object

    Returns
    -------
    Numpy array of size 3x<numper of vertices>
        Numpy array containing the vertex positions
    """
    xVerts = objBlenderobject.data.vertices
    iNVerts = len(xVerts)
    # initialize np array
    xVertices_np = np.empty([iNVerts * 3], dtype="f")
    # extract data
    xVerts.foreach_get("co", xVertices_np)
    # tranform to world coordinate system
    xVertices_np = xVertices_np.reshape([iNVerts, 3]).transpose()
    vertices_np_glob = np.array(objBlenderobject.matrix_world.to_3x3()) @ xVertices_np + np.array(
        objBlenderobject.matrix_world.to_translation()
    ).reshape(3, 1)
    return vertices_np_glob


# Enddef
def BlenderNormals2np(objBlenderobject):
    """Efficient extraction of Vertex normals to a Numpy array

    Parameters
    ----------
    objBlenderobject : Blender object

    Returns
    -------
    Numpy array of size 3x<numper of vertices>
        Numpy array containing the vertex normals
    """
    verts = objBlenderobject.data.vertices
    n_verts = len(verts)
    # initialize np array
    normals_np = np.empty([n_verts * 3], dtype="f")
    verts.foreach_get("normal", normals_np)
    normals_np = normals_np.reshape([n_verts, 3]).transpose()
    normals_np_glob = np.array(objBlenderobject.matrix_world.to_3x3()) @ normals_np
    # normals_np_glob=normals_np.reshape([3,n_verts])    without transform
    return normals_np_glob


# Enddef
def BlenderVertexindices2np(objBlenderobject):
    """Efficient extraction of Vertex indices to a numpy array

    Parameters
    ----------
    objBlenderobject : Blender object

    Returns
    -------
    Numpy array of length <numper of vertices>
        Numpy array containing the vertex indices
    """
    verts = objBlenderobject.data.vertices
    n_verts = len(verts)
    indices_np = np.empty([n_verts], dtype="int")
    verts.foreach_get("index", indices_np)
    return indices_np


# Enddef
def MultiplyVertexGroups(xMesh, sVG1, sVG2, sTargetVectorGroupName):
    """Replace all the weights in sTargetVectorGroupName by the product of the weights of xVG1 and xVG2
    if sTargetVectorGroupName does not exist, it is created

    Parameters
    ----------
    xMesh : Blender Mesh
        Persons.Plane Grid
    xVG1 : Blender Vertex Group
        First group to be merged
    xVG2 : Blender Vertex Group
        Second group to be merged
    sTargetVectorGroupName : string
        Name of the target Vertex Group
    """

    xVG1 = xMesh.vertex_groups[sVG1]
    xVG2 = xMesh.vertex_groups[sVG2]

    # Remove target vertex group if it already exists
    if sTargetVectorGroupName in xMesh.vertex_groups.keys():
        xMesh.vertex_groups.remove(xMesh.vertex_groups[sTargetVectorGroupName])
    # Endif
    VG_target = xMesh.vertex_groups.new(name=sTargetVectorGroupName)

    # Add product of the weights for all
    for v in xMesh.data.vertices:
        if xVG1.index in [v.group for v in v.groups]:
            fValueGroup1 = xVG1.weight(v.index)
        else:
            fValueGroup1 = 0.0
        # Endif
        if xVG2.index in [v.group for v in v.groups]:
            fValueGroup2 = xVG2.weight(v.index)
        else:
            fValueGroup2 = 0.0
        # Endif
        VG_target.add([v.index], fValueGroup1 * fValueGroup2, "ADD")
    # Endfor


# Enddef
def GeneratePlacementMap(objAssetPlane, fR=0.4, fH=1.8, sVertexGroupName="AnyCam.geometric_placement_mask"):
    """Create a Vector group with weights indicating whether an asset of radius fR and height fH can be placed(1.0)
    or not (0.0) considering the geometry of the scene.
    Note that all modifiers need to be applied for this algorithm to work,
    typical examples are subdivisions of the AssetPlane or shrinkwrapped camera locations!
    Args:
        objPersonsPlane (_type_): Blender Grid objectS
        fR (float, optional): Radius of the assets to be placed in meters. Defaults to 0.4.
        fH (float, optional): Height of the assets to be placed in meters. Defaults to 1.8.
        sVertexGroupName (str, optional): _description_. Name of the vertex group to be generated.
            Defaults to "AnyCam.geometric_placement_mask".
    """
    fFactor = BlenderUnitsPerMeterFactor()
    fR_bu = fR * fFactor
    fH_bu = fH * fFactor

    # Hide plane from viewport, otherwise the cast rays hit the plane itself
    objAssetPlane.hide_viewport = True

    objPersonsMesh = objAssetPlane.data
    xPersonsVert = [v for v in objPersonsMesh.vertices]

    # If vertex group already exists, remove it
    if sVertexGroupName in objAssetPlane.vertex_groups.keys():
        objAssetPlane.vertex_groups.remove(objAssetPlane.vertex_groups[sVertexGroupName])
    # Endif

    # create vertex group and initialize weights as 1.0, i.e. objects can be placed
    objMask = objAssetPlane.vertex_groups.new(name=sVertexGroupName)
    objMask.add([v.index for v in xPersonsVert], 1.0, "ADD")

    # Idea: iterate all Objects in the scene, duplicate persons.plane and intersect with object
    # to generate obstacles for the ray casting
    # Not sure how to do it with the blender api, for know, manual inspection and
    # targeted intersection with copies of the persons.plane

    xPersonsVert_np_glob = BlenderVerts2np(objAssetPlane)
    xPersonsNormals_np_glob = BlenderNormals2np(objAssetPlane)

    n_verts = xPersonsNormals_np_glob.shape[1]

    weights = np.zeros([n_verts], dtype=float)
    for i in range(n_verts):
        xRayOrigin = xPersonsVert_np_glob[:, i]
        xRayOrigin_v = mathutils.Vector(xPersonsVert_np_glob[:, i])

        xRayDir_v = mathutils.Vector(xPersonsNormals_np_glob[:, i])

        bResult, _, _, _, _, _ = bpy.context.scene.ray_cast(
            bpy.context.evaluated_depsgraph_get(),
            xRayOrigin_v,
            xRayDir_v,
            distance=fH_bu,
        )
        if bResult:
            # Ray hit something
            weights[np.linalg.norm(xPersonsVert_np_glob - xRayOrigin.reshape([3, 1]), axis=0) < fR_bu] = 1.0
        # endif
    # endfor

    # write weights
    indices = BlenderVertexindices2np(objAssetPlane)
    objMask.add([int(indices[i]) for i in np.where(weights)[0]], 0.0, "REPLACE")

    # revert hiding of the plane
    objAssetPlane.hide_viewport = False
    objAssetPlane.select_set(True)


# Enddef
def GeneratePlacementMaps(clnAssetPlaneCollection, fR=0.4, fH=1.8, sVertexGroupName="geometric_placement_mask"):
    """Convenience function applying GeneratePlacementMap to all asset planes
    in the collection clnAssetPlaneCollection passed, see documentation of GeneratePlacementMap
    """
    for objPlane in clnAssetPlaneCollection.all_objects:
        GeneratePlacementMap(objPlane, fR, fH, sVertexGroupName)
    # Endfor


# Enddef
# Some cams are not attached to an empty, for future anycam integration, better to pass the vertex of the optical center
# idea Gauss distribution instead of 0-1 assignment
def GenerateVisibilityMap(
    objAssetPlane,
    objCamOrigin,
    clnObstacles,
    fR=0.4,
    sVertexGroupName="camera_visibility_mask",
    fFovVertical=180.0,
    fFovHorizontal=180.0,
):
    """Generate vertex group with weights indicating whether an asset placed on the asset_plane at this vertex would
       be visible on a camera at the location of given empty origin, w.r.t the obstacles in obstacle_collection.
       All objects not in clnObstacles are ignored, this allows placement behind smaller, non building infrastructure
       objects such that assets can be placed partially occluded.
       Placement of assets intersecting with objects not included in clnObstacles is automatically prevented by using
       the geometric placement map generated by GeneratePlacementMap
       Note that all modifiers need to be evaluated/applied for this algorithm to work,
       typical examples are subdivisions of the AssetPlane or shrinkwrapped camera locations!
    Args:
        objAssetPlane (_type_): Grid object
        objCamOrigin (Empty): Empty object indicating the camera location
        clnObstacles (_type_): Collection of obstacles
        fR (float, optional): _description_. Radius of the asset to be placed. Defaults to 0.4.
        sVertexGroupName (str, optional): Name of the Vertex group to be generated. Defaults to "Visibility_mask".
        fFov: (int, optional): Field of View of the camera. Defaults to 180
    """
    fFov = max(fFovHorizontal, fFovVertical)
    xCamPosition_v = objCamOrigin.location
    xCamPosition = np.array(xCamPosition_v)

    # R needs to be chosen based on the resolution of the grid and the size of the asset
    fFactor = BlenderUnitsPerMeterFactor()
    fR_bu = fR * fFactor

    # hide all objects
    lHideViewportBackup = {x.name: x.hide_viewport for x in bpy.data.objects}
    for x in bpy.data.objects:
        x.hide_viewport = True
    # Endfor

    # Show all objects in the obstacle collection
    for x in clnObstacles.all_objects:
        x.hide_viewport = False
    # Endfor

    # If vertex group already exists, remove it
    if sVertexGroupName in objAssetPlane.vertex_groups.keys():
        objAssetPlane.vertex_groups.remove(objAssetPlane.vertex_groups[sVertexGroupName])
    # Endif
    objMask = objAssetPlane.vertex_groups.new(name=sVertexGroupName)

    xPersonsVert_np_glob = BlenderVerts2np(objAssetPlane)
    iNVerts = xPersonsVert_np_glob.shape[1]

    xWeights = np.zeros([iNVerts], dtype=float)

    for iLoopIndex in range(iNVerts):
        xRayOrigin = xPersonsVert_np_glob[:, iLoopIndex]
        xRayOrigin_v = mathutils.Vector(xPersonsVert_np_glob[:, iLoopIndex])
        xRayDir_v = xCamPosition_v - xRayOrigin_v
        # check if v is within the field of view of the camera, otherwise no ray cast necessary
        xCamDirection = -np.array(objCamOrigin.matrix_world)[0:3, 2]
        fAngle = (
            np.arccos(np.dot(-xRayDir_v, xCamDirection) / (np.linalg.norm(xRayDir_v) * np.linalg.norm(xCamDirection)))
            / (2 * np.pi)
            * 360
        )
        if fAngle < fFov / 2:  # Vertex within FOV, thus proceed
            fMaxDistance = 0.99 * np.linalg.norm(
                xCamPosition - xRayOrigin
            )  # Avoid hitting and registering the camera as obstacle
            bObjectHit, _, _, _, _, _ = bpy.context.scene.ray_cast(
                bpy.context.evaluated_depsgraph_get(),
                xRayOrigin_v,
                xRayDir_v,
                distance=fMaxDistance,
            )
            if not bObjectHit:
                # Ray hit nothing
                xWeights[np.linalg.norm(xPersonsVert_np_glob - xRayOrigin.reshape([3, 1]), axis=0) < fR_bu] = 1.0
            # Endif
        # Endif
    # Endfor

    # write weights into vertex group
    xIndices = BlenderVertexindices2np(objAssetPlane)
    objMask.add([int(xIndices[i]) for i in np.where(xWeights)[0]], 1.0, "ADD")

    # Show everything again
    for sName, bViewport in lHideViewportBackup.items():
        bpy.data.objects[sName].hide_viewport = bViewport
    # Endfor
    objAssetPlane.select_set(True)


# Enddef
def GenerateVisibilityMaps(
    clnAssetPlanes,
    objOrigin,
    clnObstacles,
    fR=0.4,
    sVertexGroupName="camera_visibility_mask",
    fFovVertical=180.0,
    fFovHorizontal=180.0,
):
    """Convenience function applying GenerateVisibilityMap to all asset planes
    in the collection clnAssetPlaneCollection passed, see documentation of GenerateVisibilityMap
    """
    for objPlane in clnAssetPlanes.all_objects:
        GenerateVisibilityMap(objPlane, objOrigin, clnObstacles, fR, sVertexGroupName, fFovVertical, fFovHorizontal)
    # Endfor


# Enddef
