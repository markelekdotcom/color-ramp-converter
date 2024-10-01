![ColorRampConverter](docs/images/colorrampconverter_index.png)

[![Blender 4.0](https://img.shields.io/badge/Blender-4.0.0-blue.svg)](https://www.blender.org/) 
![GitHub](https://img.shields.io/github/license/markelekdotcom/color-ramp-converter?color=blue)
[![Documentation Status](https://readthedocs.org/projects/colorrampconverter/badge/?version=latest)](https://colorrampconverter.readthedocs.io/en/latest/?badge=latest)
![Maintenance](https://img.shields.io/maintenance/yes/2024)
![GitHub issues](https://img.shields.io/github/issues-raw/markelekdotcom/color-ramp-converter)

# Color Ramp Converter
 is a <a href="https://www.blender.org/" target="_blank">Blender</a> addon that generates custom <a href="https://docs.blender.org/manual/en/latest/interface/controls/nodes/groups.html" target="_blank">node groups</a> from <a href="https://docs.blender.org/manual/en/latest/render/shader_nodes/converter/color_ramp.html" target="_blank">color ramp nodes</a>, making a few parameters more accessible.
Read more: <a href="https://colorrampconverter.readthedocs.io/en/latest/" target="_blank">Documentation</a> 

# Releases are Available:

- ## 🛒 on <a href="https://davidelek.gumroad.com/l/colorrampconverter" target="_blank">Gumroad</a>

- ## 🛒 on <a href="https://blendermarket.com/products/colorrampconverter" target="_blank">Blender Market</a>

- ## 🛒 on <a href="https://www.artstation.com/a/20894561" target="_blank">Artstation</a>

# Features

- Quickly convert between custom node group solution and color ramp node.

    ![ColorRampConverter](docs/images/dynamic_conversion_feature.gif)
    
- Connected links are managed automatically by the addon.

- The created node group is NOT dependent on the addon.
Additional features like that may be added as experimental options.

- Map range node based node group setup.
    
    ![ColorRampConverter](docs/images/node_group_inside.png)

- Constant interpolation type support with a different node group setup.

    ![ColorRampConverter](docs/images/node_group_inside_v2.png)

- Automatically add extra nodes of chosen type to the color inputs of custom node groups.
    
    ![ColorRampConverter](docs/images/extra_nodes_feature.gif)

- Remove extra nodes when converting back to color ramp node (optional) 

- The custom node group can accept any color input, not just color nodes specifically.

    ![ColorRampConverter](docs/images/color_input.gif)

- Shader editor support

- Compositor editor support

- Geometry node editor support

- <a href="https://colorrampconverter.readthedocs.io/en/latest/" target="_blank">Documentation</a> 

# Workflow

- Use color ramp nodes initially due to their intuitive controls.

- Convert to a custom node group to obtain additional control.

- Effortlessly convert back from node group to color ramp node if necessary.