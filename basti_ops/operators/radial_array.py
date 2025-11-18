import math

import bmesh
import bpy
from mathutils import Vector, Quaternion

from ..utils.object import duplicate_object
from ..utils.selection import (
    get_mesh_selection_mode,
    get_selected_bm_vertices,
    set_mesh_selection_mode,
    get_linked_verts,
)
from ..utils.mesh import duplicate_bmesh_geometry


class BastiRadialArray(bpy.types.Operator):
    """.radial_array
    Create a ring of copies of the selection.
    * pivot: the pivot to rotate around
    * axis: the axis to rotate around
    * count: how many copies to add
    * islands: when in edit mode duplicate the whole mesh island instead of just the selection
    * linked: when in object mode duplicate duplicate the objects linked to the same data
    """

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
    islands: bpy.props.BoolProperty(default=False)
    linked: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None and context.active_object.type == "MESH"
        )

    def execute(self, context):
        selection_mode = get_mesh_selection_mode(context)
        active_object = context.active_object
        rotation_pivot = Vector()
        if self.pivot == "PIVOT":
            rotation_pivot = active_object.location
        elif self.pivot == "CURSOR":
            rotation_pivot = context.scene.cursor.location
        rotation_rad = 2 * math.pi / self.count
        rotation_axis = Vector(
            (
                1.0 if self.axis == "X" else 0.0,
                1.0 if self.axis == "Y" else 0.0,
                1.0 if self.axis == "Z" else 0.0,
            )
        )

        if selection_mode == "OBJECT":
            rotation_pivot_offest = rotation_pivot - active_object.location
            for i in range(1, self.count):
                new_obj = duplicate_object(active_object, self.linked)
                with bpy.context.temp_override(
                    active_object=new_obj, selected_objects=[new_obj]
                ):
                    bpy.ops.transform.translate(value=rotation_pivot_offest)
                    bpy.ops.transform.rotate(
                        value=rotation_rad * i, orient_axis=self.axis
                    )
                    new_position_offset = -rotation_pivot_offest
                    new_position_offset.rotate(
                        Quaternion(rotation_axis, rotation_rad * i)
                    )
                    bpy.ops.transform.translate(value=new_position_offset)
            return {"FINISHED"}

        bm = bmesh.from_edit_mesh(active_object.data)
        selected_verts = get_selected_bm_vertices(bm, active_object)
        if self.islands:
            selected_verts = get_linked_verts(active_object, bm, selected_verts)

        for i in range(1, self.count):
            new_verts = duplicate_bmesh_geometry(bm, selected_verts)
            for vert in new_verts:
                coords = active_object.matrix_world @ vert.co.copy()
                coords -= rotation_pivot
                coords.rotate(Quaternion(rotation_axis, rotation_rad * i))
                coords += rotation_pivot
                vert.co = active_object.matrix_world.inverted() @ coords

        bmesh.update_edit_mesh(active_object.data)
        bm.free()

        set_mesh_selection_mode("OBJECT")
        set_mesh_selection_mode(selection_mode)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "count")
        layout.prop(self, "pivot")
        layout.prop(self, "axis")

        selection_mode = get_mesh_selection_mode(context)
        if selection_mode == "OBJECT":
            layout.prop(self, "linked")
        else:
            layout.prop(self, "islands")
