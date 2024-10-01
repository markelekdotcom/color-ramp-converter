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

from bpy.utils import register_class, unregister_class
from bpy.types import Panel
from . functions import get_addon_prefs
from . functions import any_converted_node_group
from . functions import any_color_ramp_node
from . functions import get_node_group_type


class NODE_PT_convert(Panel):
    """
    The panel for the addon
    """
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Node"
    bl_label = "Color Ramp Converter"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        """
        Draw panel layout
        """
        scene = context.scene
        addon_prefs = get_addon_prefs()

        selected_nodes = context.selected_nodes
        num_selected_nodes = len(selected_nodes)
        any_node_group_selected = any_converted_node_group(selected_nodes)
        any_color_ramp_selected = any_color_ramp_node(selected_nodes)

        layout = self.layout
        layout.operator('wm.color_ramp_converter',
                        text="CONVERT")
        if num_selected_nodes == 0 or not any((any_node_group_selected,
                                               any_color_ramp_selected)):
            layout.label(text="No nodes selected")
            layout.label(text="Select Color Ramp(s)", icon='ERROR')
            layout.label(text="Select Converted Group(s)",
                         icon='ERROR')

        if num_selected_nodes > 1:
            layout.label(text="Multiple nodes selected!", icon='INFO')

        if any_node_group_selected:
            layout.label(text="Node Group -> Color Ramp")

        if any_color_ramp_selected:
            active_node_tree = context.space_data.edit_tree
            node_tree_type = get_node_group_type(active_node_tree)

            layout.label(text="Color Ramp -> Node Group")

            if (node_tree_type in ['Geometry', 'Shader']):
                layout.label(text="Interpolation type:")
                layout.prop(scene, 'node_group_interpolation', text="")

            layout.label(text="Extra Node Type:")

            if (node_tree_type == 'Shader'):
                layout.prop(scene, "extra_shader_node_type", text="")
            elif (node_tree_type == 'Compositor'):
                layout.prop(scene, "extra_compositor_node_type", text="")
            elif (node_tree_type == 'Geometry'):
                layout.prop(scene, "extra_geometry_node_type", text="")
            layout.prop(addon_prefs, "create_extra_nodes", toggle=True)


classes = [NODE_PT_convert]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
