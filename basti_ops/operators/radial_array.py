import math

import bmesh
import bpy

from ..utils.selection import (
    mesh_selection_mode,
    get_selected_bm_vertices,
    set_mesh_selection_mode,
)
from ..utils.mesh import duplicate_bmesh_geometry


class BastiRadialArray(bpy.types.Operator):
    """Duplicate selected faces around the cursor"""

    bl_idname = "basti.radial_array"
    bl_label = "Radial Array"
    bl_options = {"REGISTER", "UNDO"}

    pivot: bpy.props.EnumProperty(
        name="Pivot",
        items=[
            ("ORIGIN", "Origin", "World Origin"),
            ("PIVOT", "Pivot", "Object Pivot"),
            ("CURSOR", "Cursor", "3d Cursor"),
        ],
        default="ORIGIN",
    )
    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z"),
        ],
        default="Z",
    )
    count: bpy.props.IntProperty(default=4)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
            and mesh_selection_mode(context) == "FACE"
        )

    def execute(self, context):
        from mathutils import Matrix, Vector

        active_object = context.active_object
        rotation_pivot = Vector()
        if self.pivot == "PIVOT":
            rotation_pivot = active_object.location
        elif self.pivot == "CURSOR":
            rotation_pivot = context.scene.cursor.location
        rotation_rad = 2 * math.pi / self.count

        bm = bmesh.from_edit_mesh(active_object.data)
        selected_verts = get_selected_bm_vertices(bm, active_object)
        for i in range(1, self.count):
            new_verts = duplicate_bmesh_geometry(bm, selected_verts)
            for vert in new_verts:
                coords = active_object.matrix_world @ vert.co.copy()
                coords -= rotation_pivot
                coords = coords @ Matrix.Rotation(rotation_rad * i, 4, self.axis)
                coords += rotation_pivot
                vert.co = active_object.matrix_world.inverted() @ coords

        bmesh.update_edit_mesh(active_object.data)
        bm.free()

        set_mesh_selection_mode("OBJECT")
        set_mesh_selection_mode("FACE")
        return {"FINISHED"}
