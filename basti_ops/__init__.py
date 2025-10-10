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

import importlib

from . import basti_ops
from . import basti_menus
from . import utils

modules = [
    utils,
    basti_ops,
    basti_menus,
]


def register():
    for m in modules:
        importlib.reload(m)
        if hasattr(m, 'register'):
            m.register()


def unregister():
    for m in reversed(modules):
        if hasattr(m, 'register'):
            m.unregister()

if __name__ == "__main__":
    register()