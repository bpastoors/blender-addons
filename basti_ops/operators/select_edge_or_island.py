import bpy

from ..utils.selection import (
    mesh_selection_mode,
    select_by_id,
    set_mesh_selection_mode,
    get_all_linked_verts,
)


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
            obj = context.active_object
            select_by_id(
                obj,
                "VERT",
                get_all_linked_verts(obj, get_index=True),
                clear_selection=False,
            )
            set_mesh_selection_mode("OBJECT")
            set_mesh_selection_mode(selection_mode)
        return {"FINISHED"}
