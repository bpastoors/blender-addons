from typing import Optional
from math import radians

import bpy
import bmesh
from mathutils import Vector, Quaternion

from ..utils.selection import (
    get_linked_verts,
    get_mesh_selection_mode,
    get_selected_polygons,
    get_selected_vertices,
    select_by_id,
    get_selected,
)
from ..utils.mesh import get_average_location, get_average_normal, rotate_vertices
from ..utils.raycast import raycast


class BastiMoveToFace(bpy.types.Operator):
    """.move_to_face
    Move the selected object or mesh island to the point on a face pointing at with the mouse. Can target the same or other meshes.
    When in edit mode, not just the selection, but all linked elements will be moved.
    * orient: in object mode the object can be rotated to align with the face normal
    * spin: spin around the normal that you oriented to
    """

    bl_idname = "basti.move_to_face"
    bl_label = "Move to Face"
    bl_options = {"REGISTER", "UNDO"}

    orient: bpy.props.BoolProperty(default=False)
    spin: bpy.props.FloatProperty(name="Spin", default=0.0)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        self.move_to_face(context, self.coords)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)

    def move_submeshes_to_point(
        self,
        objs: list[bpy.types.Mesh],
        location: Vector,
        selection_mode: str,
        normal: Optional[Vector] = None,
    ):
        """Move submeshes to the point and rotate them to the normal"""
        obj_data = []
        average_location = Vector((0.0, 0.0, 0.0))

        for obj in objs:
            selection_ids = get_selected(obj, selection_mode, get_index=True)
            selected_vert_ids = get_selected_vertices(obj, get_index=True)
            linked_vert_ids = get_linked_verts(obj, get_index=True)
            bm = bmesh.from_edit_mesh(obj.data)
            bm_verts_island = [bm.verts[v_id] for v_id in linked_vert_ids]

            average_location_obj = get_average_location(
                [bm.verts[v_id] for v_id in selected_vert_ids], obj
            )
            if normal and selection_mode == "FACE":
                average_normal = get_average_normal(get_selected_polygons(obj), obj)
                rotation_difference = average_normal.rotation_difference(normal * -1)
                rotate_vertices(
                    bm_verts_island, rotation_difference, average_location_obj, obj
                )

            average_location += average_location_obj

            obj_data.append(
                {
                    "object": obj,
                    "island_ids": linked_vert_ids,
                    "selection_ids": selection_ids,
                }
            )
            bm.free()

        average_location /= len(objs)
        move_offset = average_location - location

        for obj_data_entry in obj_data:
            obj = obj_data_entry["object"]
            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            verts = [bm.verts[i] for i in obj_data_entry["island_ids"]]
            for vert in verts:
                vert_location = obj.matrix_world @ vert.co.copy()
                vert_location -= move_offset
                vert.co = obj.matrix_world.inverted() @ vert_location

            if normal and self.spin != 0.0:
                rotate_vertices(verts, (normal, radians(self.spin)), location, obj)

            bm.normal_update()
            bmesh.update_edit_mesh(obj.data)
            bm.free()
            select_by_id(obj, selection_mode, obj_data_entry["selection_ids"])

    def move_objects_to_point(
        self,
        objs: list[bpy.types.Object],
        location: Vector,
        normal: Optional[Vector] = None,
    ):
        """Move and orient meshes to the point and rotate them to the normal"""
        average_location = Vector((0.0, 0.0, 0.0))

        for obj in objs:
            average_location += obj.location

        average_location /= len(objs)
        move_offset = average_location - location

        for obj in objs:
            obj.location -= move_offset
            if normal:
                difference = Vector((0.0, 0.0, 1.0)).rotation_difference(normal)

                if self.spin != 0.0:
                    difference.rotate(Quaternion(normal, radians(self.spin)))

                obj.rotation_euler = difference.to_euler()

    def move_to_face(self, context, coords):
        raycast_result, location, normal, _, obj_target = raycast(context, coords)
        if not raycast_result:
            return
        selection_mode = get_mesh_selection_mode(context)
        obj_active = context.active_object
        objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]

        if not self.orient:
            normal = None

        if selection_mode == "OBJECT":
            self.move_objects_to_point(objs_selected, Vector(location), normal)
        else:
            if len(objs_selected) == 0:
                objs_selected = [obj_active]
            self.move_submeshes_to_point(
                objs_selected, Vector(location), selection_mode, normal
            )

        bpy.context.view_layer.objects.active = obj_active
