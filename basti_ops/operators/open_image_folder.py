import webbrowser
from pathlib import PurePosixPath, Path

import bpy


class BastiOpenImageFolder(bpy.types.Operator):
    """.open_image_folder
    Open the source folders of the images in selected image nodes or the active image in the image editor
    """

    bl_idname = "basti.open_image_folder"
    bl_label = "Open Image Folder"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        images = None

        if hasattr(context.space_data, "image") and context.space_data.image:
            images = [context.space_data.image]
        else:
            if hasattr(context, "selected_nodes") and context.selected_nodes:
                shader_nodes = context.selected_nodes
            else:
                try:
                    obj = context.active_object
                    shader_nodes = [obj.active_material.node_tree.nodes.active]
                except AttributeError:
                    shader_nodes = None

            if shader_nodes:
                images = [
                    n.image for n in shader_nodes if n.bl_idname == "ShaderNodeTexImage"
                ]

        if not images:
            return {"FINISHED"}

        paths = set()
        for image in images:
            path = Path(image.filepath)
            if path.exists() and path.is_file():
                paths.add(path)

        path_start = PurePosixPath("File://")
        for path in paths:
            webbrowser.open(str(path_start / path.parent.as_posix()))

        return {"FINISHED"}
