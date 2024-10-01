# ##### BEGIN GPL LICENSE BLOCK #####
#
# GPLv3 License
#
# ColorRampConverter
# Copyright (C) 2022-2024, Mark Elek, David Elek
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
from bpy.types import Operator
import traceback
from .functions import *


class WM_OT_ColorRampConverter(Operator):
    """
    Operator that converts color ramp nodes to custom node group alternatives and vice versa
    """
    bl_idname = "wm.color_ramp_converter"
    bl_label = "Convert Color Ramp or MapRangeGroup"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """
        Check if any selected node is a valid node to convert
        """
        return any_valid_node(context.selected_nodes)

    def execute(self, context):
        """
        Convert color ramp nodes to custom node group alternatives and vice versa
        """
        # = context.active_object.active_material.node_tree
        active_node_tree = context.space_data.edit_tree
        selected_nodes = context.selected_nodes

        try:
            for selected_node in selected_nodes:
                if is_color_ramp(selected_node):
                    color_ramp = selected_node
                    convert_color_ramp(
                        self, context, color_ramp, active_node_tree)

                elif is_node_group(selected_node):
                    node_group = selected_node
                    convert_node_group(node_group, active_node_tree)

        # catch *all* exceptions
        except Exception as err:
            traceback.print_exc()
            return {'CANCELLED'}

        return {'FINISHED'}


class WM_OT_ResetSettings(Operator):
    """
    Operator to reset all addon preferences to default values
    """
    bl_label = "Reset ColorRampConverter Preferences"
    bl_idname = "wm.reset_settings"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        """
        Reset all addon preferences to default values
        """
        addon_prefs = get_addon_prefs()
        props = addon_prefs.__annotations__.keys()
        for p in props:
            addon_prefs.property_unset(p)
        return {'FINISHED'}

    def invoke(self, context, event):
        """
        Confirm resetting all add-on preferences
        """
        return context.window_manager.invoke_confirm(self, event)


classes = [
    WM_OT_ColorRampConverter,
    WM_OT_ResetSettings,

]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
