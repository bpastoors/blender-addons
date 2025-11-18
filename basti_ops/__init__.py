bl_info = {
    "name": "basti_operators",
    "author": "Bastian",
    "description": "",
    "blender": (4, 5, 0),
    "version": (0, 2, 0),
    "location": "",
    "warning": "",
    "category": "Generic",
}


def get_modules_from_subfolders(folders: list[str]):
    from importlib import import_module
    from pathlib import Path

    found_modules = []
    for folder in folders:
        module_path = Path(__file__).parent / folder

        if not (module_path.exists() and module_path.is_dir()):
            continue
        for file_path in module_path.glob("*.py"):
            module_name = f".{folder}.{file_path.stem}"
            try:
                module = import_module(module_name, package=__package__)
                found_modules.append(module)
            except ImportError as e:
                print(f"Failed to import {module_name}: {e}")

    return found_modules


def get_module_classes(module):
    import inspect
    from bpy import types

    class_types = [types.Menu, types.Panel, types.Operator]
    return [
        t[1]
        for t in inspect.getmembers(module, inspect.isclass)
        if any(issubclass(t[1], class_type) for class_type in class_types)
    ]


modules = get_modules_from_subfolders(["utils", "operators", "menus"])


def register():
    from importlib import reload
    from bpy.utils import register_class

    for m in modules:
        reload(m)
        classes = get_module_classes(m)
        for c in classes:
            register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for m in modules:
        classes = get_module_classes(m)
        for c in classes:
            unregister_class(c)


if __name__ == "__main__":
    register()
