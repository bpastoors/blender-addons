import bpy
import bmesh

from ..utils.mesh import duplicate_bmesh_geometry, AllLinkedVerts
from ..utils.selection import (
    select_by_id,
    mesh_selection_mode,
    set_mesh_selection_mode,
    get_all_selected_vertices,
)


class BastiQuickMirror(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.quick_mirror"
    bl_label = "Quick Mirror"
    bl_options = {"REGISTER", "UNDO"}

    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z"),
        ],
        default="X",
    )
    delete_target: bpy.props.EnumProperty(
        name="Delete Target Side",
        items=[
            ("NO", "No", "No"),
            ("LINKED", "Linked", "Linked"),
            ("ALL", "All", "All"),
        ],
        default="LINKED",
    )
    auto_merge: bpy.props.BoolProperty(
        name="Automatic Merge",
        default=True,
    )
    auto_merge_distance: bpy.props.FloatProperty(
        name="Automatic Merge Distance",
        default=0.0001,
    )

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
        )

    def execute(self, context):
        axis_int = 0
        if self.axis != "X":
            axis_int += 1 if self.axis == "Y" else 2

        selection_mode = mesh_selection_mode(context)
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        bm_verts_selected = [bm.verts[v.index] for v in get_all_selected_vertices(obj)]
        average_location = sum([v.co[axis_int] for v in bm_verts_selected]) / len(
            bm_verts_selected
        )
        if self.delete_target != "NO":
            deletion_side = -1 if average_location > 0 else 1
            verts_to_check = (
                AllLinkedVerts(bm_verts_selected).execute()
                if self.delete_target == "LINKED"
                else bm.verts
            )
            verts_to_delete = [
                v for v in verts_to_check if v.co[axis_int] * deletion_side > 0
            ]
            for vert in verts_to_delete:
                if vert in bm_verts_selected:
                    bm_verts_selected.remove(vert)
            bmesh.ops.delete(bm, geom=verts_to_delete)

        bm_verts_duplicated = duplicate_bmesh_geometry(
            bm,
            AllLinkedVerts(bm_verts_selected).execute(),
        )

        for vert in bm_verts_duplicated:
            vert.co[axis_int] *= -1.0

        bmesh.update_edit_mesh(obj.data)
        bm.free()

        if self.auto_merge:
            select_by_id(obj, "VERT", [v.index for v in bm_verts_duplicated], True)
            bpy.ops.mesh.remove_doubles(
                threshold=self.auto_merge_distance, use_unselected=True
            )

        set_mesh_selection_mode("OBJECT")
        set_mesh_selection_mode(selection_mode)
        return {"FINISHED"}
