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
import bpy
from cathenv import env2 as cathenv

sPathScript = r"[path]"
# sPathScript = r"[path]"
cathenv.Init(sPathScript=sPathScript)

from anyblend import util

lNodeGroups = ["AT.Func.MaterialLabelValue"]

util.node.MakeMaterialNodeGroupsUnique(lNodeGroups)
