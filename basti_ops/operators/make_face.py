import bpy

from ..utils.selection import (
    mesh_selection_mode,
    get_all_selected_vertices,
    get_all_selected_edges,
    set_mesh_selection_mode,
    select_open_border_loop,
    get_linked_edges,
)


class BastiMakeFace(bpy.types.Operator):
    """Creates a new face to fill a hole"""

    bl_idname = "basti.make_face"
    bl_label = "Make Face"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
        )

    def execute(self, context):
        submesh_mode = mesh_selection_mode(context)
        obj = context.active_object

        if submesh_mode == "VERT":
            selected_verts = get_all_selected_vertices(obj)
            linked_edges = get_linked_edges(obj, selected_verts)
            if not (
                len(selected_verts) == 3
                and len(
                    [
                        edge
                        for edge in linked_edges
                        if all(
                            vert_index in [v.index for v in selected_verts]
                            for vert_index in edge.vertices
                        )
                    ]
                )
            ):
                select_open_border_loop(obj, linked_edges)

        elif submesh_mode == "EDGE":
            selected_edges = get_all_selected_edges(obj)
            if not (
                len(selected_edges) == 2
                and len({v for e in selected_edges for v in e.vertices}) == 3
            ):
                select_open_border_loop(obj, selected_edges)

        bpy.ops.mesh.edge_face_add()
        set_mesh_selection_mode("FACE")
        return {"FINISHED"}

        # elif submesh_mode == "FACE":
        return {"FINISHED"}
