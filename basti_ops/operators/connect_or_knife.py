import bpy

from ..utils.selection import (
    mesh_selection_mode,
    get_all_selected_vertices,
)


class BastiConnectOrKnife(bpy.types.Operator):
    bl_idname = "basti.connect_or_knife"
    bl_label = "Connects two selected vertices or invokes knife tool"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        return (
            context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
        )

    def execute(self, context):
        selection_mode = mesh_selection_mode(context)
        if (
            selection_mode == "VERT"
            and len(get_all_selected_vertices(context.active_object)) == 2
        ):
            bpy.ops.mesh.vert_connect()
        else:
            bpy.ops.mesh.knife_tool("INVOKE_DEFAULT")
        return {"FINISHED"}
