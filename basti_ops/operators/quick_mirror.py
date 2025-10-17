import bpy
import bmesh
from mathutils import Vector

from ..utils.mesh import duplicate_bmesh_geometry
from ..utils.selection import (
    select_by_id,
    mesh_selection_mode,
    set_mesh_selection_mode,
    get_bmesh_islands_verts_from_selection,
)


class BastiQuickMirror(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.quick_mirror"
    bl_label = "Quick Mirror"
    bl_options = {"REGISTER", "UNDO"}

    axis: bpy.props.EnumProperty(
        items=[
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z"),
        ],
        default="X",
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
        selection_mode = mesh_selection_mode(context)
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        bm_verts_duplicated = duplicate_bmesh_geometry(
            bm,
            get_bmesh_islands_verts_from_selection(obj, bm),
        )

        value = Vector(
            (
                -1.0 if self.axis == "X" else 1.0,
                -1.0 if self.axis == "Y" else 1.0,
                -1.0 if self.axis == "Z" else 1.0,
            )
        )
        for vert in bm_verts_duplicated:
            vert.co *= value

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
