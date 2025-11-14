import bpy
import bmesh

from ..utils.mesh import duplicate_bmesh_geometry
from ..utils.selection import (
    select_by_id,
    get_mesh_selection_mode,
    set_mesh_selection_mode,
    get_selected_bm_vertices,
    get_linked_verts,
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
    pivot: bpy.props.EnumProperty(
        name="Pivot",
        items=[
            ("ORIGIN", "Origin", "World Origin"),
            ("PIVOT", "Pivot", "Object Pivot"),
            ("CURSOR", "Cursor", "3d Cursor"),
        ],
        default="ORIGIN",
    )
    scope: bpy.props.EnumProperty(
        name="Scope",
        items=[
            ("SELECTED", "Selected", "Selected"),
            ("ISLAND", "Island", "Island"),
            ("ALL", "All", "All"),
        ],
        default="ISLAND",
    )
    delete_target: bpy.props.EnumProperty(
        name="Delete Target Side",
        items=[
            ("NO", "No", "No"),
            ("ISLAND", "Island", "Island"),
            ("ALL", "All", "All"),
        ],
        default="ISLAND",
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

        def get_offset_coords(vert: bmesh.types.BMVert):
            coords = vert.co.copy()
            if self.pivot == "PIVOT":
                return coords
            coords = obj.matrix_world @ coords
            if self.pivot == "CURSOR":
                coords[axis_int] -= context.scene.cursor.location[axis_int]
            return coords

        selection_mode = get_mesh_selection_mode(context)
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)

        bm_verts_selected = get_selected_bm_vertices(bm, obj)
        average_location = sum(
            [get_offset_coords(v)[axis_int] for v in bm_verts_selected]
        ) / len(bm_verts_selected)
        if self.delete_target != "NO":
            deletion_side = -1 if average_location > 0 else 1
            verts_to_check = (
                get_linked_verts(obj, bm, bm_verts_selected)
                if self.delete_target == "ISLAND"
                else bm.verts
            )
            verts_to_delete = [
                v
                for v in verts_to_check
                if get_offset_coords(v)[axis_int] * deletion_side
                > self.auto_merge_distance
            ]
            for vert in verts_to_delete:
                if vert in bm_verts_selected:
                    bm_verts_selected.remove(vert)
            bmesh.ops.delete(bm, geom=verts_to_delete)

        bm_verts_to_duplicate = (
            get_linked_verts(obj, bm, bm_verts_selected)
            if self.scope == "ISLAND"
            else bm_verts_selected if self.scope == "SELECTED" else list(bm.verts)
        )
        bm_verts_duplicated = duplicate_bmesh_geometry(bm, bm_verts_to_duplicate, True)

        for vert in bm_verts_duplicated:
            coords = get_offset_coords(vert)

            coords[axis_int] *= -1.0

            if self.pivot in ["ORIGIN", "CURSOR"]:
                if self.pivot == "CURSOR":
                    coords[axis_int] += context.scene.cursor.location[axis_int]
                coords = obj.matrix_world.inverted() @ coords
            vert.co = coords

        bmesh.update_edit_mesh(obj.data)
        bm.free()

        if self.auto_merge:
            select_by_id(obj, "VERT", [v.index for v in bm_verts_duplicated])
            bpy.ops.mesh.remove_doubles(
                threshold=self.auto_merge_distance, use_unselected=True
            )

        set_mesh_selection_mode("OBJECT")
        set_mesh_selection_mode(selection_mode)
        return {"FINISHED"}
