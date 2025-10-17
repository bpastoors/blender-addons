import bpy

from ..utils.selection import mesh_selection_mode


class BastiSelectEdgeOrIsland(bpy.types.Operator):
    bl_idname = "basti.select_edge_or_island"
    bl_label = "Select Edge Loop or Island"
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
        if selection_mode == "EDGE":
            bpy.ops.mesh.loop_multi_select(ring=False)
        if selection_mode in ["FACE", "VERT"]:
            bpy.ops.mesh.select_linked()
        return {"FINISHED"}
