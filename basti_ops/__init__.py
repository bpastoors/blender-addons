import importlib

from . import basti_ops


bl_info = {
    "name": "basti_operators",
    "author": "Bastian",
    "description": "",
    "blender": (2, 93, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}

modules = [
    basti_ops
]


def register():
    for m in modules:
        importlib.reload(m)
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister