#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_rigidbody_object_pars.py
# Created Date: Thursday, November 10th 2022, 3:46:15 pm
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

import enum
from anybase import assertion


class ERigidBodyType(enum.Enum):
    ACTIVE = enum.auto()
    PASSIVE = enum.auto()


# endclass


class ECollisionShape(enum.Enum):
    CONVEX_HULL = enum.auto()
    MESH = enum.auto()
    SPHERE = enum.auto()


# endclass


class EMeshSource(enum.Enum):
    BASE = enum.auto()
    DEFORM = enum.auto()
    FINAL = enum.auto()


# endclass


class CRigidBodyObjectPars:

    _iCollisionCollectionCount: int = 20

    def __init__(self, *, _objX=None):

        self.eType: ERigidBodyType = ERigidBodyType.ACTIVE
        self.fMass: float = 1.0
        self.bEnabled: bool = True
        self.bKinematic: bool = False
        self.eCollisionShape: ECollisionShape = ECollisionShape.CONVEX_HULL
        self.eMeshSource: EMeshSource = EMeshSource.DEFORM
        self.bUseDeform: bool = False
        self.fFriction: float = 0.5
        self.fRestitution: float = 0.0
        self.bUseMargin: bool = False
        self.fCollisionMargin: float = 0.04
        self.fLinearDamping: float = 0.04
        self.fAngularDamping: float = 0.1
        self._lCollisionCollections: list[bool] = [
            x == 0 for x in range(CRigidBodyObjectPars._iCollisionCollectionCount)
        ]

        if _objX is not None and _objX.rigid_body is not None:
            self.InitFromObject(_objX)
        # endif

    # enddef

    @property
    def iCollisionCollectionCount(self):
        return CRigidBodyObjectPars._iCollisionCollectionCount

    # enddef

    @property
    def lCollisionCollections(self) -> list[bool]:
        return self._lCollisionCollections.copy()

    # enddef

    @lCollisionCollections.setter
    def lCollisionCollections(self, _lValue: list[bool]):
        assertion.IsList(_lValue, "Given collsion collection value is not a list")

        bValue: bool
        for iIdx, bValue in enumerate(_lValue):
            assertion.IsBool(bValue, f"Value at index '{iIdx}' in collision collection list is not a boolean")

            self._lCollisionCollections[iIdx] = bValue
        # endfor

    # enddef

    @property
    def lCollisionCollectionIndices(self) -> list[int]:
        return [i for i, x in enumerate(self._lCollisionCollections) if x is True]

    # enddef

    @lCollisionCollectionIndices.setter
    def lCollisionCollectionIndices(self, _lValue: list[int]):
        assertion.IsList(_lValue, "Given collision collection value is not a list")

        self._lCollisionCollections = [x in _lValue for x in range(CRigidBodyObjectPars._iCollisionCollectionCount)]

    # enddef

    @property
    def sType(self) -> str:
        if self.eType == ERigidBodyType.ACTIVE:
            return "ACTIVE"
        elif self.eType == ERigidBodyType.PASSIVE:
            return "PASSIVE"
        else:
            raise RuntimeError(f"Unsupported rigid body type '{self.eType}'")
        # endif

    # enddef

    @sType.setter
    def sType(self, _sValue: str):
        sValue = _sValue.upper()
        if sValue == "ACTIVE":
            self.eType = ERigidBodyType.ACTIVE
        elif sValue == "PASSIVE":
            self.eType = ERigidBodyType.PASSIVE
        else:
            raise RuntimeError(f"Unsupported rigid body type '{sValue}'")
        # endif

    # enddef

    @property
    def sCollisionShape(self) -> str:
        if self.eCollisionShape == ECollisionShape.CONVEX_HULL:
            return "CONVEX_HULL"
        elif self.eCollisionShape == ECollisionShape.MESH:
            return "MESH"
        elif self.eCollisionShape == ECollisionShape.SPHERE:
            return "SPHERE"
        else:
            raise RuntimeError(f"Unsupported collision shape '{self.eCollisionShape}'")
        # endif

    # enddef

    @sCollisionShape.setter
    def sCollisionShape(self, _sValue: str):
        sValue = _sValue.upper()
        if sValue == "CONVEX_HULL":
            self.eCollisionShape = ECollisionShape.CONVEX_HULL
        elif sValue == "MESH":
            self.eCollisionShape = ECollisionShape.MESH
        elif sValue == "SPHERE":
            self.eCollisionShape = ECollisionShape.SPHERE
        else:
            raise RuntimeError(f"Unsupported collision shape '{sValue}'")
        # endif

    # enddef

    @property
    def sMeshSource(self) -> str:
        if self.eMeshSource == EMeshSource.BASE:
            return "BASE"
        elif self.eMeshSource == EMeshSource.DEFORM:
            return "DEFORM"
        elif self.eMeshSource == EMeshSource.FINAL:
            return "FINAL"
        else:
            raise RuntimeError(f"Unsupported mesh source '{self.eMeshSource}'")
        # endif

    # enddef

    @sMeshSource.setter
    def sMeshSource(self, _sValue: str):
        sValue = _sValue.upper()
        if sValue == "BASE":
            self.eMeshSource = EMeshSource.BASE
        elif sValue == "DEFORM":
            self.eMeshSource = EMeshSource.DEFORM
        elif sValue == "FINAL":
            self.eMeshSource = EMeshSource.FINAL
        else:
            raise RuntimeError(f"Unsupported mesh source '{sValue}'")
        # endif

    # enddef

    # ########################################################################################
    def InitFromObject(self, _objX):

        rbX = _objX.rigid_body
        if rbX is None:
            raise RuntimeError(f"Object '{_objX.name}' has no rigid body information")
        # endif

        self.sType = rbX.type

        self.fMass = rbX.mass
        self.bEnabled = rbX.enabled
        self.bKinematic = rbX.kinematic
        self.sCollisionShape = rbX.collision_shape
        self.sMeshSource = rbX.mesh_source

        self.bUseDeform = rbX.use_deform
        self.fFriction = rbX.friction
        self.fRestitution = rbX.restitution
        self.bUseMargin = rbX.use_margin
        self.fCollisionMargin = rbX.collision_margin
        self.fLinearDamping = rbX.linear_damping
        self.fAngularDamping = rbX.angular_damping

        self._lCollisionCollections = list(rbX.collision_collections)

    # enddef

    # ########################################################################################
    def ApplyToObject(self, _objX):
        rbX = _objX.rigid_body
        if rbX is None:
            raise RuntimeError(f"Object '{_objX.name}' has no rigid body information")
        # endif

        rbX.type = self.sType

        rbX.mass = self.fMass
        rbX.enabled = self.bEnabled
        rbX.kinematic = self.bKinematic

        rbX.collision_shape = self.sCollisionShape
        rbX.mesh_source = self.sMeshSource

        rbX.use_deform = self.bUseDeform
        rbX.friction = self.fFriction
        rbX.restitution = self.fRestitution
        rbX.use_margin = self.bUseMargin
        rbX.collision_margin = self.fCollisionMargin
        rbX.linear_damping = self.fLinearDamping
        rbX.angular_damping = self.fAngularDamping

        for i in range(len(self._lCollisionCollections)):
            rbX.collision_collections[i] = self._lCollisionCollections[i]
        # endfor

    # enddef


# endclass
