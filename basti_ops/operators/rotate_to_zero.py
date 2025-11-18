from math import radians

import bpy
import bmesh
from mathutils import Vector

from ..utils.selection import (
    get_linked_verts,
    get_mesh_selection_mode,
    set_mesh_selection_mode,
    get_selected_polygons,
    get_selected_vertices,
)
from ..utils.mesh import get_average_location, get_average_normal, rotate_vertices


class BastiRotateToZero(bpy.types.Operator):
    """.rotate_to_zero
    Rotate the submesh so that the face selection is aligned with an axis
    * axis: the axis to align with
    * flip: flip the direction of the target axis
    * spin: spin the submesh around the axis"""

    bl_idname = "basti.rotate_to_zero"
    bl_label = "Rotate to Zero"
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
    flip: bpy.props.BoolProperty(name="Flip", default=False)
    spin: bpy.props.FloatProperty(name="Spin", default=0.0)

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        return (
            context.active_object.type == "MESH"
            and get_mesh_selection_mode(context) == "FACE"
        )

    def execute(self, context):
        obj = context.active_object
        selected_faces = get_selected_polygons(obj)
        if not selected_faces:
            return {"FINISHED"}

        average_normal = get_average_normal(selected_faces, obj)

        target_direction = Vector(
            (
                1.0 if self.axis == "X" else 0.0,
                1.0 if self.axis == "Y" else 0.0,
                1.0 if self.axis == "Z" else 0.0,
            )
        )
        if average_normal.dot(target_direction) < average_normal.dot(-target_direction):
            target_direction = -target_direction
        if self.flip:
            target_direction = -target_direction

        rotation_difference = average_normal.rotation_difference(target_direction)

        selected_vertices = get_selected_vertices(obj)
        average_location = get_average_location(selected_vertices, obj)
        linked_vertices = get_linked_verts(
            obj, seed_verts=selected_vertices, get_index=True
        )

        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        verts = [bm.verts[i] for i in linked_vertices]

        rotate_vertices(
            verts,
            rotation_difference,
            average_location,
            obj,
        )
        if self.spin != 0.0:
            rotate_vertices(
                verts, (target_direction, radians(self.spin)), average_location, obj
            )

        bmesh.update_edit_mesh(obj.data)
        bm.free()

        set_mesh_selection_mode("OBJECT")
        set_mesh_selection_mode("FACE")
        return {"FINISHED"}
