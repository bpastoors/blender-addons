import bpy

from ..utils.selection import (
    get_mesh_selection_mode,
    select_shared_edges_from_polygons,
    get_selected_edges,
    get_selected_vertices,
    select_by_id,
    select_edges_between_vertices,
)


class BastiLoopSlice(bpy.types.Operator):
    """.loop_slice
    Get the edge ring or face loop based on the selection and subdivide them. Then enter the edge sliding tool if only one edge has been added.
    * Multi: whether to add one edge and slide it or add multiple
    * Count: how many edges to add in multi-mode"""

    bl_idname = "basti.loop_slice"
    bl_label = "Loop Slice"
    bl_options = {"REGISTER", "UNDO"}

    multi: bpy.props.BoolProperty(name="Multi", default=False)
    count: bpy.props.IntProperty(name="Count", default=1, min=1)

    @classmethod
    def poll(cls, context):
        if not context.active_object or context.active_object.type != "MESH":
            return False
        selection_mode = get_mesh_selection_mode(context)
        return selection_mode in ["EDGE", "FACE"]

    def execute(self, context):
        selection_mode = get_mesh_selection_mode(context)
        obj = context.active_object

        if selection_mode == "FACE":
            try:
                select_shared_edges_from_polygons(obj)
            except RuntimeError:
                return {"CANCELLED"}

        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.mesh.subdivide_edgering(number_cuts=self.count, interpolation="LINEAR")

        obj.update_from_editmode()
        selected_edges = get_selected_edges(obj)
        selected_edges_ids = [e.index for e in selected_edges]
        selected_edges_keys = [e.key for e in selected_edges]
        selected_vert_ids = get_selected_vertices(obj, get_index=True)

        verts_ids_to_select = list(
            {
                v_index
                for key in selected_edges_keys
                for v_index in key
                if v_index not in selected_vert_ids
            }
        )

        select_by_id(obj, "VERT", verts_ids_to_select)
        select_edges_between_vertices(obj)
        select_by_id(obj, "EDGE", selected_edges_ids, deselect=True)

        if not self.multi:
            bpy.ops.transform.edge_slide("INVOKE_DEFAULT")
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "multi")
        if self.multi:
            layout.prop(self, "count")
