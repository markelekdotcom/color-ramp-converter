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

import bpy
from bpy.props import BoolProperty
from bpy.props import EnumProperty
from bpy.props import StringProperty


def extra_shader_node_type_items(self, context):
    """
    Returns a list of shader node types to pick from for extra nodes

    :param context: context
    :type context:  bpy.types.Context
    :return: list of node types to pick from for extra nodes
    :rtype: list of tuples (string, string, string)
    """
    return [
        ('ShaderNodeRGB', 'RGB', ""),
        ('ShaderNodeMixRGB', 'MixRGB', "")
    ]


def extra_compositor_node_type_items(self, context):
    """
    Returns a list of compositor node types to pick from for extra nodes

    :param context: context
    :type context:  bpy.types.Context
    :return: list of node types to pick from for extra nodes
    :rtype: list of tuples (string, string, string)
    """
    return [
        ('CompositorNodeRGB', 'RGB', ""),
        ('CompositorNodeMixRGB', 'MixRGB', ""),
    ]


def extra_geometry_node_type_items(self, context):
    """
    Returns a list of geometry node types to pick from for extra nodes

    :param context: context
    :type context:  bpy.types.Context
    :return: list of node types to pick from for extra nodes
    :rtype: list of tuples (string, string, string)
    """
    return [
        ('FunctionNodeInputColor', 'RGB', ""),
        ('ShaderNodeMixRGB', 'MixRGB', ""),
    ]


def node_group_interpolation_items(self, context):
    """
    Returns a list of map range node interpolation types to pick from for custom node group

    :param context: context
    :type context: bpy.types.Context
    :return: list of interpolation types to pick from for custom node group
    :rtype: list of tuples (string, string, string)
    """
    return [
        ('LINEAR', 'Linear', "Linear interpolation between From Min and From Max values"),
        ('STEPPED', 'Stepped Linear',
         "Stepped linear interpolation between From Min and From Max values"),
        ('SMOOTHSTEP', 'Smooth Step',
         "Smooth Hermite edge interpolation between From Min and From Max values"),
        ('SMOOTHERSTEP', 'Smoother Step',
         "Smoother Hermite edge interpolation between From Min and From Max values"),
    ]


def register():

    bpy.types.ShaderNodeGroup.is_converted = BoolProperty(
        name="Is Converted",
        description="Is this a converted color ramp node group?",
        default=False,
    )

    bpy.types.CompositorNodeGroup.is_converted = BoolProperty(
        name="Is Converted",
        description="Is this a converted color ramp node group?",
        default=False,
    )
    bpy.types.GeometryNodeGroup.is_converted = BoolProperty(
        name="Is Converted",
        description="Is this a converted color ramp node group?",
        default=False,
    )

    bpy.types.Node.is_excess = BoolProperty(
        name="Is Excess",
        description="Is this an excess node from color ramp conversion?",
        default=False
    )

    bpy.types.Node.linked_node_group_name = StringProperty(
        name="Linked Node Group Name",
        description="Name of the linked node group",
        default="",
    )

    bpy.types.Scene.extra_shader_node_type = EnumProperty(
        name="Extra Shader Node Type",
        description="Shader node type to pick from for extra nodes",
        items=extra_shader_node_type_items,
    )

    bpy.types.Scene.extra_compositor_node_type = EnumProperty(
        name="Extra Compositor Node Type",
        description="Compositor node type to pick from for extra nodes",
        items=extra_compositor_node_type_items,
    )

    bpy.types.Scene.extra_geometry_node_type = EnumProperty(
        name="Extra Geometry Node Type",
        description="Geometry node type to pick from for extra nodes",
        items=extra_geometry_node_type_items,
    )

    bpy.types.Scene.node_group_interpolation = EnumProperty(
        name="Node Group Interpolation",
        description="The interpolation type of map range nodes in converted node groups",
        items=node_group_interpolation_items,
    )


def unregister():

    del bpy.types.ShaderNodeGroup.is_converted
    del bpy.types.CompositorNodeGroup.is_converted
    del bpy.types.GeometryNodeGroup.is_converted
    del bpy.types.Node.is_excess
    del bpy.types.Node.linked_node_group_name
    del bpy.types.Scene.extra_shader_node_type
    del bpy.types.Scene.extra_compositor_node_type
    del bpy.types.Scene.extra_geometry_node_type
    del bpy.types.Scene.node_group_interpolation
