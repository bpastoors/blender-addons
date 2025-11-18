import bpy

from ..utils.object import delete_objects
from ..utils.mesh import join_meshes


class BastiPasteFromClipboard(bpy.types.Operator):
    """.paste_from_clipboard
    Paste elements copied with **.copy_to_clipboard** into the currently selected mesh
    """

    bl_idname = "basti.paste_from_clipboard"
    bl_label = "Paste from Clipboard"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        current_mode = context.active_object.mode
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        obj_target = context.active_object
        objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]

        bpy.ops.object.select_all(action="DESELECT")

        bpy.ops.view3d.pastebuffer(autoselect=True)
        obj_copy = bpy.context.selected_objects[0]

        if not obj_copy.type == "MESH":
            delete_objects([obj_copy])
        else:
            join_meshes([obj_target, obj_copy])

        for obj in objs_selected:
            obj.select_set(True)
        bpy.ops.object.mode_set(mode=current_mode)
        return {"FINISHED"}
