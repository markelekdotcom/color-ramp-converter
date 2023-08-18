# ##### BEGIN GPL LICENSE BLOCK #####
#
# GPLv3 License
#
# ColorRampConverter
# Copyright (C) 2022, Mark Elek, David Elek
#
# ColorRampConverter is a Blender addon that generates
# custom node groups from color ramp nodes,
# making a few parameters more accessible.
#
# This file is a part of ColorRampConverter.
# ColorRampConverter is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# ColorRampConverter is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ColorRampConverter. If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

from .src import operators
from .src import panels
from .src import preferences
from .src import properties

bl_info = {
    "name": "ColorRampConverter",
    "author": "Mark Elek, David Elek",
    "description": "Convert Color Ramp node to Map Range nodes and back",
    "blender": (3, 6, 2),
    "version": (1, 2, 0),
    "location": "Shader Editor -> 'N' Sidebar -> 'Convert Color Ramp' Panel",
    "warning": "",
    "doc_url": "https://colorrampconverter.readthedocs.io/en/latest/",
    "tracker_url": "https://github.com/markelekdotcom/color-ramp-converter/issues",
    "support": "COMMUNITY",
    "category": "Node"
}


def register():
    operators.register()
    panels.register()
    preferences.register()
    properties.register()


def unregister():
    operators.unregister()
    panels.unregister()
    preferences.unregister()
    properties.unregister()
