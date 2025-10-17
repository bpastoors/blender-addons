import bpy

from ..utils.selection import select_by_id, mesh_selection_mode, select_shared_edges_from_polygons, get_all_selected_edges


class BastiSelectLoop(bpy.types.Operator):
    bl_idname = "basti.select_loop"
    bl_label = "Select Edge Loop or Face Loop"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        return context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT'

    def execute(self, context):
        selection_mode = mesh_selection_mode(context)
        if not selection_mode in ["VERT", "EDGE", "FACE"]:
            return {"FINISHED"}

        if selection_mode in ["VERT", "EDGE"]:
            bpy.ops.mesh.loop_multi_select(ring=False)
            return {"FINISHED"}

        obj = context.active_object
        try:
            select_shared_edges_from_polygons(obj)
        except RuntimeError:
            return {"CANCELLED"}

        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.object.mode_set(mode="OBJECT")
        ring_edge_keys = [e.key for e in get_all_selected_edges(obj)]
        polys_to_select = []
        for poly in obj.data.polygons:
            matched_keys = [k for k in poly.edge_keys if k in ring_edge_keys]
            if len(matched_keys) == 2:
                polys_to_select.append(poly.index)

        select_by_id(obj, "FACE", polys_to_select, deselect=True)

        return {"FINISHED"}
