from math import radians
from random import uniform, seed

import bmesh
import bpy
from mathutils import Vector, Euler

from ..utils.object import duplicate_object
from ..utils.selection import (
    select_by_id,
    get_mesh_selection_mode,
    get_selected_bm_vertices,
    set_mesh_selection_mode,
    get_linked_verts,
)
from ..utils.mesh import duplicate_bmesh_geometry, get_average_location


class BastiScatterDuplicate(bpy.types.Operator):
    """Scatter Duplicate selection"""

    bl_idname = "basti.scatter_duplicate"
    bl_label = "Scatter Duplicate"
    bl_options = {"REGISTER", "UNDO"}

    count: bpy.props.IntProperty(default=1)
    offset: bpy.props.FloatVectorProperty()
    add_negative_offset: bpy.props.BoolProperty(default=False)
    rotation: bpy.props.FloatVectorProperty()
    add_negative_rotation: bpy.props.BoolProperty(default=False)
    seed: bpy.props.IntProperty(default=1)
    islands: bpy.props.BoolProperty(default=True)
    linked: bpy.props.BoolProperty(default=False)

    min_offset = (0.0, 0.0, 0.0)
    min_rotation = (0.0, 0.0, 0.0)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None and context.active_object.type == "MESH"
        )

    def get_new_offset_and_rotation(self):
        return Vector(
            [
                uniform(self.min_offset[0], self.offset[0]),
                uniform(self.min_offset[1], self.offset[1]),
                uniform(self.min_offset[2], self.offset[2]),
            ]
        ), Euler(
            [
                radians(uniform(self.min_rotation[0], self.rotation[0])),
                radians(uniform(self.min_rotation[1], self.rotation[1])),
                radians(uniform(self.min_rotation[2], self.rotation[2])),
            ]
        )

    def execute(self, context):
        seed(self.seed)
        selection_mode = get_mesh_selection_mode(context)
        active_object = context.active_object
        if self.add_negative_offset:
            self.min_offset = (-self.offset[0], -self.offset[1], -self.offset[2])
        if self.add_negative_rotation:
            self.min_rotation = (
                -self.rotation[0],
                -self.rotation[1],
                -self.rotation[2],
            )

        if selection_mode == "OBJECT":
            for i in range(1, self.count):
                new_obj = duplicate_object(active_object, self.linked)
                new_offset, new_rotation = self.get_new_offset_and_rotation()
                if new_obj.rotation_mode == "QUATERNION":
                    new_obj.rotation_quaternion.rotate(new_rotation)
                else:
                    new_obj.rotation_euler.rotate(new_rotation)
                new_obj.location = new_obj.location + new_offset

            return {"FINISHED"}

        bm = bmesh.from_edit_mesh(active_object.data)
        selected_verts = get_selected_bm_vertices(bm, active_object)
        if self.islands:
            selected_verts = get_linked_verts(active_object, bm, selected_verts)

        average_location = get_average_location(selected_verts, active_object)
        vert_selection_extension = []
        for i in range(1, self.count):
            new_offset, new_rotation = self.get_new_offset_and_rotation()
            new_verts = duplicate_bmesh_geometry(bm, selected_verts)
            for vert in new_verts:
                location = active_object.matrix_world @ vert.co.copy()
                location -= average_location
                location.rotate(new_rotation)
                location += average_location + new_offset
                vert.co = active_object.matrix_world.inverted() @ location
            vert_selection_extension.extend(new_verts)

        selected_verts.extend(vert_selection_extension)

        vert_ids = [v.index for v in selected_verts]
        bmesh.update_edit_mesh(active_object.data)

        set_mesh_selection_mode("OBJECT")
        select_by_id(active_object, "VERT", vert_ids)
        set_mesh_selection_mode("OBJECT")
        set_mesh_selection_mode(selection_mode)
        bm.free()
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "count")
        layout.prop(self, "offset")
        layout.prop(self, "add_negative_offset")
        layout.prop(self, "rotation")
        layout.prop(self, "add_negative_rotation")
        layout.prop(self, "seed")

        selection_mode = get_mesh_selection_mode(context)
        if selection_mode == "OBJECT":
            layout.prop(self, "linked")
        else:
            layout.prop(self, "islands")
