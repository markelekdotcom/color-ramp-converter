# ##### BEGIN GPL LICENSE BLOCK #####
#
# GPLv3 License
#
# ColorRampConverter
# Copyright (C) 2022-2025, Mark Elek, David Elek
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

import bpy
from bpy.types import AddonPreferences
from bpy.props import (BoolProperty,
                       )


class Preferences(AddonPreferences):
    bl_idname = 'color-ramp-converter'

    copy_width: BoolProperty(
        name="Copy Width",
        description="Copy the width of initial node or node group",
        default=True
    )

    create_extra_nodes: BoolProperty(
        name="Create Extra Nodes",
        description="Create extra nodes for the converted node group's inputs",
        default=False
    )

    remove_extra_nodes: BoolProperty(
        name="Remove Extra Nodes",
        description="Remove extra nodes when converting back to color ramp",
        default=True
    )
    
    legacy_const_ramp_conv: BoolProperty(
        name="Legacy Constant Ramp Conversion",
        description="Uses color ramps instead of map range nodes.",
        default=False
    )

    def draw(self, context):
        layout = self.layout

        '''Generic Settings'''
        box = layout.box()
        row = box.row()
        row.prop(self, "copy_width")
        row = box.row()
        row.prop(self, "create_extra_nodes")
        row = box.row()
        row.prop(self, "remove_extra_nodes")
        row.enabled = self.create_extra_nodes
        
        box = layout.box()
        row = box.row()
        row.prop(self, "legacy_const_ramp_conv")
        warning_row = box.row()
        warning_row.label(text="Does NOT generate position inputs for constant interpolation node groups!", icon='ERROR')

        row = layout.row()
        row.scale_y = 1.5
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("wm.reset_settings")


classes = [Preferences]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
