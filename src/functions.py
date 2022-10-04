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
import contextlib


def get_addon_prefs():
    """
    Get addon preferences

    :return: Addon preferences
    :rtype: bpy.types.AddonPreferences
    """
    return bpy.context.preferences.addons['color-ramp-converter'].preferences


def clamp_value(value, min_value, max_value):
    """
    Clamp a value to a minimum and maximum value

    :param value: The value to clamp
    :type value: int or float
    :param min_value: The minimum value
    :type min_value: int or float
    :param max_value: The maximum value
    :type max_value: int or float
    :return: The clamped value
    :rtype: int or float
    """
    return max(min_value, min(value, max_value))


def is_color_ramp(node):
    """
    Check if node is a color ramp node

    :param node: The node to check
    :type node: bpy.types.Node
    :return: Returns True if node is a color ramp node, False otherwise
    :rtype: bool
    """
    class_name = node.__class__.__name__
    return class_name in ['ShaderNodeValToRGB', 'CompositorNodeValToRGB']


def is_node_group(node):
    """
    Check if node is a converted node group

    :param node: The node to check
    :type node: bpy.types.Node
    :return: Returns True if node is a converted node group, False otherwise
    :rtype: bool
    """
    return (node.__class__.__name__
            in ['ShaderNodeGroup', 'CompositorNodeGroup', 'GeometryNodeGroup']
            and node.is_converted)


def is_map_range(node):
    """
    Check if node is a map range node

    :param node: The node to check
    :type node: bpy.types.Node
    :return: Returns True if node is a map range node, False otherwise
    :rtype: bool
    """
    return node.__class__.__name__ in ['ShaderNodeMapRange', 'CompositorNodeMapRange']


def is_mix_rgb(node):
    """
    Check if node is a mix rgb node

    :param node: The node to check
    :type node: bpy.types.Node
    :return: Returns True if node is a mix rgb node, False otherwise
    :rtype: bool
    """
    return node.__class__.__name__ in ['ShaderNodeMixRGB', 'CompositorNodeMixRGB']


def is_node_group_input_node(node):
    """
    Check if node is a node group input node

    :param node: The node to check
    :type node: bpy.types.Node
    :return: Returns True if node is a node group input node, False otherwise
    :rtype: bool
    """
    return node.__class__.__name__ == 'NodeGroupInput'


def is_group_output(node):
    """
    Check if node is a node group output node

    :param node: The node to check
    :type node: bpy.types.Node
    :return: Returns True if node is a node group output node, False otherwise
    :rtype: bool
    """
    return node.__class__.__name__ == 'NodeGroupOutput'


def is_valid_node(node):
    """
    Check if node is a valid node to be used in the color ramp converter

    :param node: The node to check
    :type node: bpy.types.Node
    :return: Returns True if node is a valid node, False otherwise
    :rtype: bool
    """
    if node is None:
        return False
    elif is_color_ramp(node):
        color_count = len(node.color_ramp.elements)
        return color_count > 1
    elif not is_node_group(node):
        return False
    elif not node.is_converted:
        return False

    return True


def any_color_ramp_node(nodes):
    """
    Check if any node in the list is a color ramp node

    :param nodes: The list of nodes to check
    :type nodes: list of bpy.types.Node
    :return: Returns True if any node is a color ramp node, False otherwise
    :rtype: bool
    """
    return any(is_color_ramp(node) for node in nodes)


def any_converted_node_group(nodes):
    """
    Check if any node in the list is a converted node group

    :param nodes: The list of nodes to check
    :type nodes: list of bpy.types.Node
    :return: Returns True if any node is a converted node group, False otherwise
    :rtype: bool
    """
    return any(is_node_group(node) for node in nodes)


def any_valid_node(nodes):
    """
    Check if any node in the list is a valid node

    :param nodes: The list of nodes to check
    :type nodes: list of bpy.types.Node
    :return: Returns True if any node is a valid node, False otherwise
    :rtype: bool
    """
    return any(is_valid_node(node) for node in nodes)


def set_node_location(node, location):
    """
    Set the location of a node in the shader node editor

    :param node: The node to set the location of
    :type node: bpy.types.Node
    :param location: The location to set the node to
    :type location: float array of 2 items in [-100000, 100000]
    """
    node.location = location


def get_node_group_height(node_group):
    """
    Get the (estimated) height of a node group

    :param node_group: The node group to get the height of
    :type node_group: bpy.types.NodeGroup
    :return: The estimated height of the node group
    :rtype: int
    """
    num_inputs = len(node_group.inputs)
    estimated_height = (num_inputs//6) * (node_group.height)
    num_remaining_inputs = num_inputs % 6
    estimated_height += (node_group.height/6) * num_remaining_inputs
    return (num_inputs*(node_group.height/6.25))


def offset_node_location_y(node, amount=100.0, space=-100.0, delta=-1):
    """
    Offset the location of node on the y axis by (amount + space) * delta

    :param node: The node to offset the location of
    :type node: bpy.types.Node
    :param amount: The amount to offset the location by
    :type amount: float in [-inf, inf], default 100.0, optional
    :param space: Extra space to add between created nodes
    :type space: float in [-300.0, 20.0], default -100.0, optional
    :param delta: The delta to apply to the offset (offset * delta)
    :type delta: int -1 or 1, optional
    """
    clamped_space = clamp_value(space, -300.0, 20.0)
    node.location.y += (amount+clamped_space)*delta


def offset_node_location_x(node, node_width=0.0, space=100.0, delta=-1):
    """
    Offset the location of node on the x axis by (node_width + space) * delta

    :param node: The node to offset the location of
    :type node: bpy.types.Node
    :param node_width: The width of the color ramp node
    :type node_width: float in [-inf, inf], default 0.0
    :param space: Extra space to add between created nodes
    :type space: float in [50, 200], default 100.0, optional
    :param delta: The delta to apply to the offset (offset * delta)
    :type delta: int -1 or 1, optional
    """
    clamped_space = clamp_value(space, 50, 200)
    node.location.x += (node_width+clamped_space)*delta


def set_node_width(node, width=0.0):
    """
    Set the width of a node in the shader node editor

    :param node: The node to set the width of
    :type node: bpy.types.Node
    :param width: The width to set the node to
    :type width: float in [-inf, inf], default 0.0
    """
    node.width = width


def remove_node(node_to_delete, from_node_tree):
    """
    Remove a node from a node tree

    :param node_to_delete: The node to delete
    :type node_to_delete: bpy.types.Node
    :param from_node_tree: The node tree to remove the node from
    :type from_node_tree: bpy.types.NodeTree
    """
    from_node_tree.nodes.remove(node_to_delete)


def create_node_group_input(node_group, socket_type, socket_name, value):
    """
    Create inputs (sockets) for converted node group

    :param node_group: The node group to create the inputs for
    :type node_group: bpy.types.NodeGroup
    :param socket_type: Thy type of the input socket to create
    :type socket_type: str in ['NodeSocketColor', 'NodeSocketFloat']
    :param socket_name: The name of the input socket to create
    :type socket_name: str
    :param value: Default value of the created input socket
    :type value: float or float array of 4 items in [0.0, 1.0]
    :return: Returns the created input socket
    :rtype: bpy.types.NodeSocket
    """
    assert socket_type in [
        'NodeSocketColor', 'NodeSocketFloat'], (
            "Invalid socket type!"
            "Should be str in ['NodeSocketColor', 'NodeSocketFloat'] !")

    node_group_input = node_group.inputs.new(socket_type, socket_name)
    node_group_input.default_value = value
    return node_group_input


def set_or_create_node_group_input(node_group, socket_type, socket_name, value):
    """
    Set or create inputs (sockets) for converted node group

    :param node_group: The node group to set (if exists) or create the inputs for
    :type node_group: bpy.types.NodeGroup
    :param socket_type: Thy type of the input socket to set or create
    :type socket_type: str in ['NodeSocketColor', 'NodeSocketFloat']
    :param socket_name: The name of the input socket to set or create
    :type socket_name: str
    :param value: Default value of the created input socket
    :type value: float array of 4 items in [0.0, 1.0], default 0.0
    :return: Returns the created input socket
    :rtype: bpy.types.NodeSocket
    """
    assert socket_type in [
        'NodeSocketColor', 'NodeSocketFloat'], (
            "Invalid socket type!"
            "Should be str in ['NodeSocketColor', 'NodeSocketFloat'] !")

    existing_input = node_group.inputs.get(socket_name)
    if existing_input is not None:
        existing_input.default_value = value
        return existing_input
    create_node_group_input(node_group, socket_type, socket_name, value)
    return existing_input


def create_node(node_group, node_type, node_name, location=(0.0, 0.0)):
    """
    Create a node in a node group

    :param node_group: The node group to create the node in
    :type node_group: bpy.types.NodeGroup
    :param node_type: The type of the node to create
    :type node_type: bpy.types.Node
    :param node_name: The name of the node to create
    :type node_name: str
    :param location: The location of the node
    :type location: float array of 2 items in [-100000, 100000], default (0.0, 0.0)
    :return: Returns the created node
    :rtype: bpy.types.Node
    """
    node = node_group.nodes.new(node_type)
    set_node_name(node, node_name)
    set_node_location(node, location)
    return node


def get_or_create_node(node_group, node_type, node_name, location=(0.0, 0.0)):
    """
    Get node if it exists in the node group, otherwise create it

    :param node_group: The node group to get or create the node in
    :type node_group: bpy.types.NodeGroup
    :param node_type: The type of the node to get or create
    :type node_type: bpy.types.Node
    :param node_name: The name of the node to get or create
    :type node_name: str
    :param location: The location of the node
    :type location: float array of 2 items in [-100000, 100000], default (0.0, 0.0)
    :return: Returns the created node
    :rtype: bpy.types.Node
    """
    existing_node = node_group.nodes.get(node_name)
    if existing_node is not None:
        existing_node.is_excess = False
        return existing_node
    created_node = create_node(node_group, node_type, node_name, location)
    created_node.is_excess = False
    return created_node


def mark_nodes_as_excess(nodes):
    """
    When reusing shader node trees, mark unused nodes as excess to know which ones to remove

    :param nodes: The nodes to mark as excess (node group input and output nodes are not marked)
    :type nodes: list of bpy.types.Node
    """
    for node in nodes:
        if not is_node_group_input_node(node) and not is_group_output(node):
            node.is_excess = True


def set_node_name(node, name):
    """
    Set the name of a node

    :param node: The node to set the name of
    :type node: bpy.types.Node
    :param name: The name to set the node's name to
    :type name: str
    """
    node.name = name


def set_node_label(node, label):
    """
    Set the label of a node

    :param node: The node to set the label of
    :type node: bpy.types.Node
    :param label: The label to set the node's label to
    :type label: str
    """
    node.label = label


def set_extra_node_linked_node_group_name(node, node_group_name):
    """
    Set the linked node group name of a node

    :param node: The node to set the linked node group name of
    :type node: bpy.types.Node
    :param node_group_name: The name of the linked node group
    :type node_group_name: str
    """
    node.linked_node_group_name = node_group_name


def set_extra_node_input_color(node, color_input, color):
    """
    Set the input color of a node

    :param node: The node to set the input color of
    :type node: bpy.types.Node
    :param color_input: The input to set the color of
    :type color_input: bpy.types.NodeSocket
    :param color: The color to set the input color to
    :type color: float array of 4 items in [0.0, 1.0]
    """
    with contextlib.suppress(Exception):
        # some nodes don't have color 'inputs'
        node.color = color

    for i in range(len(color_input.default_value)):
        color_input.default_value[i] = color[i]


def get_extra_node_color_input(extra_node):
    """
    Get the color input of a node

    :param extra_node: The node to get the color input of
    :type extra_node: bpy.types.Node
    :return: Returns the color input of the node
    :rtype: bpy.types.NodeSocket
    """
    node_input_names = [name for name in extra_node.inputs.keys()
                        if 'Color' in name
                        or 'RGBA' in name
                        or 'Image' in name]
    node_output_names = [name for name in extra_node.outputs.keys()
                         if 'Color' in name
                         or 'RGBA' in name
                         or 'Image' in name]
    if node_input_names:
        return extra_node.inputs[node_input_names[0]]
    elif node_output_names:
        return extra_node.outputs[node_output_names[0]]
    else:
        return extra_node.outputs.get('Color')


def get_extra_node_output_to_link(extra_node):
    """
    Get the output socket of extra node that needs to be linked to node group

    :param extra_node: The extra node to get the output socket of
    :type extra_node: bpy.types.Node
    :return: Returns the output socket of the extra node
    :rtype: bpy.types.NodeSocket
    """
    outputs = extra_node.outputs
    output_to_link = None
    for output in outputs:
        if 'RGBA' in output.type:
            return output
    with contextlib.suppress(IndexError):
        output_to_link = outputs[0]
    return output_to_link


def set_map_range_interpolation(map_range_node, interpolation_type):
    """
    Set the interpolation type of a map range node

    :param map_range_node: The map range node to set the interpolation type of
    :type map_range_node: bpy.types.Node
    :param interpolation_type: The interpolation type to set the map range node's interpolation type to
    :type interpolation_type: str in ['LINEAR', 'STEPPED', 'SMOOTHSTEP', 'SMOOTHERSTEP']
    """
    if hasattr(map_range_node, 'interpolation_type'):
        map_range_node.interpolation_type = interpolation_type


def remove_excess_nodes(nodes):
    """
    Remove nodes marked as excess from a list of nodes

    :param nodes: The nodes to remove excess nodes from
    :type nodes: list of bpy.types.Node
    """
    nodes_to_remove = [node for node in nodes if node.is_excess]
    for node in nodes_to_remove:
        nodes.remove(node)


def remove_excess_extra_nodes(nodes, linked_node_group_name):
    """
    Remove nodes linked to a custom node group

    :param nodes: The nodes to remove excess nodes from
    :type nodes: list of bpy.types.Node
    :param linked_node_group_name: The name of the linked node group
    :type linked_node_group_name: str
    """

    nodes_to_remove = [node for node in nodes
                       if node.linked_node_group_name == linked_node_group_name]
    for node in nodes_to_remove:
        nodes.remove(node)


def remove_excess_inputs(node_group):
    """
    Remove excess inputs from a node group when reusing shader node trees

    :param node_group: The node group to remove excess inputs from
    :type node_group: bpy.types.NodeGroup
    """
    node_group_input_node = node_group.node_tree.nodes.get('Group Input')

    socket_names = [output.name for output in node_group_input_node.outputs
                    if ((len(output.links) <= 0)
                        and ('Color' in output.name or 'Pos' in output.name))]

    for socket_name in socket_names:
        node_group.node_tree.inputs.remove(
            node_group.node_tree.inputs[socket_name])


def link_nodes(node_group):
    """
    Link all nodes in the node group in a specific way

    :param node_group: The node group to link nodes in
    :type node_group: bpy.types.NodeGroup
    """

    map_range_nodes = [
        node for node in node_group.nodes if is_map_range(node)]
    mix_rgb_nodes = [
        node for node in node_group.nodes if is_mix_rgb(node)]
    node_group_input_node = node_group.nodes.get('Group Input')
    node_group_output_node = node_group.nodes.get('Group Output')

    map_range_node_count = len(map_range_nodes)
    # link map range nodes
    for i in range(map_range_node_count):
        # link first map range node to group input node
        if i == 0 or i != map_range_node_count - 1:
            node_group.links.new(
                node_group_input_node.outputs[f'Pos{i+1}'], map_range_nodes[i].inputs[1])
            node_group.links.new(
                node_group_input_node.outputs[f'Pos{i+2}'], map_range_nodes[i].inputs[2])

        else:
            node_group.links.new(
                node_group_input_node.outputs[f'Pos{i+2}'], map_range_nodes[i].inputs[2])
            node_group.links.new(
                node_group_input_node.outputs[f'Pos{i+1}'], map_range_nodes[i].inputs[1])

        # link map range nodes value input to group input node
        node_group.links.new(
            map_range_nodes[i].inputs[0], node_group_input_node.outputs[0])

        # link map range results to fac input of mix rgb node
        node_group.links.new(
            map_range_nodes[i].outputs[0], mix_rgb_nodes[i].inputs[0])

        # link 'to max' input to map range node
        node_group.links.new(
            node_group_input_node.outputs["To Min"], map_range_nodes[i].inputs["To Min"])

        # link 'to min' input to map range node
        node_group.links.new(
            node_group_input_node.outputs["To Max"], map_range_nodes[i].inputs["To Max"])

    # link first mix rgb node's color output to group output's color input
    node_group.links.new(
        mix_rgb_nodes[0].outputs[0], node_group_output_node.inputs["Color"])

    mix_rgb_nodes_count = len(mix_rgb_nodes)
    # link other mix rgb nodes
    for i in range(mix_rgb_nodes_count):

        # link all mix rgb nodes' first color input to group input except last
        node_group.links.new(node_group_input_node.outputs[f"Color{i+1}"],
                             mix_rgb_nodes[i].inputs[1])

        # link last mix rgb node's second color input to group input
        if i == mix_rgb_nodes_count-1:
            node_group.links.new(node_group_input_node.outputs[f"Color{i+2}"],
                                 mix_rgb_nodes[i].inputs[2])
        else:
            node_group.links.new(
                mix_rgb_nodes[i].inputs[2], mix_rgb_nodes[i+1].outputs[0])


def instantiate_node_group(node_group, node_group_type, node_group_name, node_tree):
    """
    Instantiate a node group in a node tree

    :param node_group: The node group to instantiate
    :type node_group: bpy.types.NodeGroup
    :param node_group_type: The type of the node group
    :type node_group_type: str in ['Shader', 'Compositor', 'Geometry']
    :param node_group_name: The name of the node group to instantiate
    :type node_group_name: str
    :param node_tree: The node tree to instantiate the node group in
    :type node_tree: bpy.types.NodeTree
    :return: The instantiated node group
    :rtype: bpy.types.NodeGroup
    """
    dummy_group = node_tree.nodes.new(f'{node_group_type}NodeGroup')
    dummy_group.name = node_group_name
    dummy_group.label = dummy_group.name
    dummy_group.node_tree = node_group
    return dummy_group


def get_node_group_type(node_tree):
    """
    Get the type of a node group based on the type of the node tree

    :param node_tree: The node tree to get the type of
    :type node_tree: bpy.types.NodeTree
    :return: The type of the node group
    :rtype: str in ['Shader', 'Compositor', 'Geometry']
    """
    if node_tree.bl_idname == 'ShaderNodeTree':
        return 'Shader'
    elif node_tree.bl_idname == 'CompositorNodeTree':
        return 'Compositor'
    elif node_tree.bl_idname == 'GeometryNodeTree':
        return 'Geometry'
    else:
        raise TypeError(
            f'Node tree: {node_tree.name} is not a shader, compositor or geometry node tree')


def get_node_type(node_tree):
    """
    Get the type of a node, based on the type of the node tree

    :param node_tree: The node tree to get the type of
    :type node_tree: bpy.types.NodeTree
    :return: The type of the node base on the type of the node tree
    :rtype: str in ['Shader', 'Compositor']
    """
    if node_tree.bl_idname in ['ShaderNodeTree', 'GeometryNodeTree']:
        return 'Shader'
    elif node_tree.bl_idname == 'CompositorNodeTree':
        return 'Compositor'
    else:
        raise TypeError(
            f'Node tree: {node_tree.name} is not a shader, compositor or geometry node tree')


def create_node_group(node_group_name, node_tree, color_ramp, interpolation_type):
    """
    Create a custom node group from a color ramp

    :param node_group_name: The name of the node group to create
    :type node_group_name: str
    :param node_tree: The node tree to create the node group in
    :type node_tree: bpy.types.NodeTree
    :param color_ramp: The color ramp to create the node group from
    :type color_ramp: [bpy.types.ShaderNodeValToRGB, bpy.types.CompositeNodeValToRGB]
    :return: The created node group
    :rtype: bpy.types.NodeGroup
    """
    node_tree_type = get_node_type(node_tree)
    node_group_type = get_node_group_type(node_tree)
    color_ramp_elements = color_ramp.color_ramp.elements
    color_count = len(color_ramp_elements)

    value_nodes = []
    map_range_nodes = []
    mix_rgb_nodes = []

    existing_node_group = bpy.data.node_groups.get(node_group_name)
    if (existing_node_group is not None
            and existing_node_group.name == node_group_name
            # can't reuse shader node tree in compositor node tree or vice versa
            and existing_node_group.bl_idname == f'{node_tree_type}NodeTree'):

        set_or_create_node_group_input(existing_node_group, 'NodeSocketFloat',
                                       'Fac', color_ramp.inputs[0].default_value)

        # remove 'to min' and 'to max' input
        existing_node_group.inputs.remove(existing_node_group.inputs['To Min'])
        existing_node_group.inputs.remove(existing_node_group.inputs['To Max'])

        for i in range(color_count):
            # add colors of color stops as inputs to node group
            set_or_create_node_group_input(existing_node_group, 'NodeSocketColor', f'Color{i+1}',
                                           color_ramp_elements[i].color)

            # add positions of color stops as inputs to node group
            set_or_create_node_group_input(existing_node_group, 'NodeSocketFloat', f'Pos{i+1}',
                                           color_ramp_elements[i].position)

            # need one less from these nodes
            if i+1 < color_count:
                # add map range nodes
                map_range_node = get_or_create_node(existing_node_group, f'{node_tree_type}NodeMapRange',
                                                    f'Map Range{i+1}', (0, -i*300))
                set_map_range_interpolation(map_range_node, interpolation_type)
                map_range_nodes.append(map_range_node)

                # add mix rgb nodes
                mix_rgb_node = get_or_create_node(existing_node_group, f'{node_tree_type}NodeMixRGB',
                                                  f'Mix{i+1}', (200, -i*300))
                mix_rgb_nodes.append(mix_rgb_node)

        set_or_create_node_group_input(existing_node_group,
                                       'NodeSocketFloat', 'To Min', 0)
        set_or_create_node_group_input(existing_node_group,
                                       'NodeSocketFloat', 'To Max', 1)

        remove_excess_nodes(existing_node_group.nodes)

        mark_nodes_as_excess(existing_node_group.nodes)

        link_nodes(existing_node_group)

        node_group = instantiate_node_group(
            existing_node_group, node_group_type, node_group_name, node_tree)

        remove_excess_inputs(node_group)

        return node_group

    node_group = bpy.data.node_groups.new(
        node_group_name, f'{node_group_type}NodeTree')

    # add fac input to node group
    create_node_group_input(node_group, 'NodeSocketFloat',
                            'Fac', color_ramp.inputs[0].default_value)

    # add group input node
    node_group_input_node = node_group.nodes.new('NodeGroupInput')
    node_group_input_node.location = (-400, 0)

    # add group output node
    node_group_output_node = node_group.nodes.new('NodeGroupOutput')
    node_group_output_node.location = (400, 0)

    # add color input to group output node
    node_group.outputs.new('NodeSocketColor', 'Color')

    # create nodes
    for i in range(color_count):
        # add colors of color stops as inputs to node group
        color_input = node_group.inputs.new('NodeSocketColor', f'Color{i+1}')
        color_input.default_value = color_ramp_elements[i].color

        # add positions of color stops as inputs to node group
        pos_input = node_group.inputs.new('NodeSocketFloat', f'Pos{i+1}')
        pos_input.default_value = color_ramp_elements[i].position

        # need one less from these nodes
        if i+1 < color_count:
            # add map range nodes
            map_range_node = create_node(node_group, f'{node_tree_type}NodeMapRange',
                                         f'Map Range{i+1}', (0, -i*300))
            set_map_range_interpolation(map_range_node, interpolation_type)
            map_range_nodes.append(map_range_node)

            # add mix rgb nodes
            mix_rgb_node = create_node(node_group, f'{node_tree_type}NodeMixRGB',
                                       f'Mix{i+1}', (200, -i*300))
            mix_rgb_nodes.append(mix_rgb_node)

    # add 'to min' and 'to max' inputs to group input node
    create_node_group_input(node_group,
                            'NodeSocketFloat', 'To Min', 0)
    create_node_group_input(node_group,
                            'NodeSocketFloat', 'To Max', 1)

    link_nodes(node_group)

    node_group = instantiate_node_group(
        node_group, node_group_type, node_group_name, node_tree)

    return node_group


def auto_link_node_group(color_ramp, active_node_tree, node_group):
    """
    Auto link the node group to the same node sockets as the color ramp node

    :param color_ramp: The color ramp to get the links from
    :type color_ramp: [bpy.types.ShaderNodeValToRGB, bpy.types.CompositeNodeValToRGB]
    :param active_node_tree: The active node tree
    :type active_node_tree: bpy.types.NodeTree
    :param node_group: The node group to recreate the links for
    :type node_group: bpy.types.NodeGroup
    """
    # handle inputs
    if color_ramp.inputs[0].is_linked:
        color_ramp_link = color_ramp.inputs[0].links[0]
        from_node = color_ramp_link.from_node
        from_socket_name = color_ramp_link.from_socket.name
        active_node_tree.links.new(
            from_node.outputs[from_socket_name], node_group.inputs["Fac"])

    # handle outputs
    if color_ramp.outputs[0].is_linked:
        color_ramp_links = color_ramp.outputs[0].links
        for link in color_ramp_links:
            to_node = link.to_node
            to_socket_name = link.to_socket.name
            active_node_tree.links.new(
                node_group.outputs["Color"], to_node.inputs[to_socket_name])


def create_extra_nodes_for_node_group(self, node_group, node_tree, node_type, with_link=True):
    """
    Create extra nodes for the node group

    :param node_group: The node group to create the extra nodes for
    :type node_group: bpy.types.NodeGroup
    :param node_tree: The node tree to create the extra nodes in
    :type node_tree: bpy.types.NodeTree
    :param node_type: The type of node to create
    :type node_type: str
    :param with_link: Create extra nodes with links to the node group, defaults to True
    :type with_link: bool, optional
    """
    report = False
    node_tree_type = get_node_type(node_tree)
    for i in range(len(node_group.inputs)):
        ng_input = node_group.inputs[i]
        if ng_input.bl_idname == 'NodeSocketColor':
            node = node_tree.nodes.new(node_type)

            # to know which extra nodes to delete when removing the node group
            set_extra_node_linked_node_group_name(node, node_group.name)
            set_node_location(node, node_group.location)
            offset_node_location_x(
                node, node_group.width, delta=-1)
            offset_node_location_y(node, i*node.height, delta=-1)

            color_input = get_extra_node_color_input(node)

            output_to_link = get_extra_node_output_to_link(node)
            set_extra_node_input_color(
                node, color_input, ng_input.default_value)
            if output_to_link is None:
                report = True
            elif with_link:
                node_tree.links.new(output_to_link, ng_input)

    if report:
        node_type = node_type.replace(f'{node_tree_type}Node', '')
        self.report(
            {'WARNING'}, f'"{node_type} Node" has no compatible output to connect to')


def convert_color_ramp(self, context, color_ramp, node_tree):
    """
    Convert a color ramp to a custom node group alternative

    :param context: context
    :type context: bpy.context
    :param color_ramp: The color ramp to convert
    :type color_ramp: [bpy.types.ShaderNodeValToRGB, bpy.types.CompositeNodeValToRGB]
    :param node_tree: The node tree to add the node group to
    :type node_tree: bpy.types.NodeTree
    """
    scene = context.scene
    addon_prefs = get_addon_prefs()

    color_ramp_location = color_ramp.location
    node_group = create_node_group(f'Converted{color_ramp.name}', node_tree, color_ramp,
                                   scene.node_group_interpolation)
    auto_link_node_group(color_ramp, node_tree, node_group)
    if addon_prefs.copy_width:
        set_node_width(node_group, color_ramp.width)

    set_node_location(node_group, color_ramp_location)
    node_group.is_converted = True

    # override node
    remove_node(color_ramp, node_tree)

    node_tree_type = get_node_group_type(node_tree)
    if addon_prefs.create_extra_nodes:
        if node_tree_type == 'Shader':
            extra_node_type = context.scene.extra_shader_node_type
        elif node_tree_type == 'Compositor':
            extra_node_type = context.scene.extra_compositor_node_type
        elif node_tree_type == 'Geometry':
            extra_node_type = context.scene.extra_geometry_node_type

        create_extra_nodes_for_node_group(
            self, node_group, node_tree, extra_node_type)

    node_group.select = True
    node_tree.nodes.active = node_group


def create_color_ramp_node(name, node_tree, node_group):
    """
    Create a color ramp node from converted node group

    :param name: The name of the color ramp node
    :type name: str
    :param node_tree: The node tree to add the node to
    :type node_tree: bpy.types.NodeTree
    :param node_group: The node group to create the color ramp from
    :type node_group: bpy.types.NodeGroup
    :return: The created color ramp node
    :rtype: [bpy.types.ShaderNodeValToRGB, bpy.types.CompositeNodeValToRGB]
    """
    node_tree_type = get_node_type(node_tree)
    color_ramp_node = node_tree.nodes.new(type=f'{node_tree_type}NodeValToRGB')
    set_node_name(color_ramp_node, name)
    set_node_label(color_ramp_node, name)

    # set fac value
    color_ramp_node.inputs["Fac"].default_value = node_group.inputs["Fac"].default_value

    colors = []
    positions = []
    for i in range(1, len(node_group.inputs)-2):
        # add color stop to color ramp node
        if i % 2 == 1:
            colors.append(node_group.inputs[i].default_value)
        else:
            positions.append(node_group.inputs[i].default_value)

    for i in range(len(colors)):
        # create color stops if needed
        if i not in [0, len(colors) - 1]:
            color_ramp_node.color_ramp.elements.new(positions[i])
        # set color of color stops
        color_ramp_node.color_ramp.elements[i].color = colors[i]

    return color_ramp_node


def auto_link_color_ramp_node(node_group, active_node_tree, color_ramp_node):
    """
    Auto link the color ramp node to the same sockets as the converted node group

    :param node_group: The node group to get the links from
    :type node_group: bpy.types.NodeGroup
    :param active_node_tree: The active node tree
    :type active_node_tree: bpy.types.NodeTree
    :param color_ramp_node: The color ramp node to recreate the links for
    :type color_ramp_node: [bpy.types.ShaderNodeValToRGB, bpy.types.CompositeNodeValToRGB]
    """
    # handle inputs
    if node_group.inputs[0].is_linked:
        node_group_link = node_group.inputs[0].links[0]
        from_node = node_group_link.from_node
        from_socket_name = node_group_link.from_socket.name
        active_node_tree.links.new(
            from_node.outputs[from_socket_name], color_ramp_node.inputs["Fac"])

    # handle outputs
    if node_group.outputs[0].is_linked:
        node_tree_type = get_node_type(active_node_tree)
        if node_tree_type == 'Shader':
            output_key = 'Color'
        elif node_tree_type == 'Compositor':
            output_key = 'Image'
        node_group_links = node_group.outputs[0].links
        for link in node_group_links:
            to_node = link.to_node
            to_socket_name = link.to_socket.name
            active_node_tree.links.new(
                color_ramp_node.outputs[output_key], to_node.inputs[to_socket_name])


def convert_node_group(node_group, node_tree):
    """
    Convert a custom node group to a color ramp

    :param node_group: The node group to convert
    :type node_group: bpy.types.NodeGroup
    :param node_tree: The node tree to add the color ramp to
    :type node_tree: bpy.types.NodeTree
    """
    addon_prefs = get_addon_prefs()

    color_ramp_name = node_group.node_tree.name.replace(
        'Converted', '')

    color_ramp_node = create_color_ramp_node(
        color_ramp_name, node_tree, node_group)

    if addon_prefs.copy_width:
        set_node_width(color_ramp_node, node_group.width)

    auto_link_color_ramp_node(node_group, node_tree,
                              color_ramp_node)

    set_node_location(color_ramp_node, node_group.location)

    if addon_prefs.remove_extra_nodes:
        remove_excess_extra_nodes(node_tree.nodes, node_group.name)
    # override
    remove_node(node_group, node_tree)

    color_ramp_node.select = True
    node_tree.nodes.active = color_ramp_node
