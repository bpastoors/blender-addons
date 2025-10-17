import bpy

from ..utils.selection import mesh_selection_mode, select_shared_edges_from_polygons, get_all_selected_edges, select_by_id


class BastiLoopSlice(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "basti.loop_slice"
    bl_label = "Loop Slice"
    bl_options = {"REGISTER", "UNDO"}

    multi: bpy.props.BoolProperty(name="Multi", default=False)
    count: bpy.props.IntProperty(name="Count", default=1, min=1)

    @classmethod
    def poll(cls, context):
        if not context.active_object or context.active_object.type != 'MESH':
            return False
        selection_mode = mesh_selection_mode(context)
        return selection_mode in ["EDGE", "FACE"]

    def execute(self, context):
        selection_mode = mesh_selection_mode(context)
        obj = context.active_object

        if selection_mode == "FACE":
            try:
                select_shared_edges_from_polygons(obj)
            except RuntimeError:
                return {"CANCELLED"}

        obj.update_from_editmode()
        selected_edge_ids = [e.index for e in get_all_selected_edges(obj)]
        new_edge_ids = []

        for edge_id in selected_edge_ids:
            select_by_id(obj, "EDGE", [edge_id], True)
            bpy.ops.mesh.loop_multi_select(ring=True)
            bpy.ops.mesh.subdivide_edgering(number_cuts=self.count)

            obj.update_from_editmode()
            for i in range(self.count):
                new_edge_ids.append(len(obj.data.edges) - 1 - i)

        select_by_id(obj, "EDGE", new_edge_ids, True)
        bpy.ops.mesh.loop_multi_select()
        if not self.multi:
            bpy.ops.transform.edge_slide("INVOKE_DEFAULT")

        return {"FINISHED"}
