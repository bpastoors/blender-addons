import bpy
import bmesh

from ..utils.selection import mesh_selection_mode, get_all_selected_vertices


class BastiMergeToActive(bpy.types.Operator):
    """merges all selected vertices at the location of the active vertex"""

    bl_idname = "basti.merge_to_active"
    bl_label = "Merge to Active"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
            and mesh_selection_mode(context) == "VERT"
        )

    def execute(self, context):
        active_object = context.active_object
        bpy.ops.object.mode_set(mode="OBJECT")
        bm = bmesh.new()
        bm.from_mesh(active_object.data)
        bm.verts.ensure_lookup_table()

        target_vert = bm.select_history.active
        if not target_vert:
            bm.free()
            bpy.ops.object.mode_set(mode="EDIT")
            self.report({"INFO"}, "No active Vertex found to merge to")
            return {"CANCELLED"}
        target_location = target_vert.co.copy()
        selected_verts = get_all_selected_vertices(active_object)

        for i in [vert.index for vert in selected_verts]:
            bm.verts[i].co = target_location

        bm.to_mesh(active_object.data)
        bm.free()
        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.mesh.merge(type="CENTER")

        return {"FINISHED"}
