bl_info = {
    "name": "Organic Growth Generator",
    "blender": (4, 2, 0),
    "category": "Node",
    "version": (0, 1, 0),
    "author": "Francisco Santelices",
    "description": "Addon para generar estructuras orgánicas con Geometry Nodes",
}

import bpy
from .src import organic_root_generator

def register():
    organic_root_generator.register()

def unregister():
    organic_root_generator.unregister()
