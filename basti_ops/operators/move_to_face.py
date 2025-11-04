from typing import Optional

import bpy
import bmesh
from mathutils import Vector

from ..utils.selection import (
    get_linked_verts,
    get_selected_bm_vertices,
    get_mesh_selection_mode,
    set_mesh_selection_mode,
    get_selected_polygons,
)
from ..utils.mesh import get_average_location, get_average_normal
from ..utils.raycast import raycast


class BastiMoveToFace(bpy.types.Operator):
    """move selected submesh or object to face under Cursor"""

    bl_idname = "basti.move_to_face"
    bl_label = "Move to Face"
    bl_options = {"REGISTER", "UNDO"}

    orient: bpy.props.BoolProperty(default=False)

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
        normal: Optional[Vector] = None,
    ):
        """Move submeshes to the point and rotate them to the normal"""
        obj_data = []
        average_location = Vector((0.0, 0.0, 0.0))
        selection_mode = get_mesh_selection_mode(bpy.context)

        for obj in objs:
            bm = bmesh.from_edit_mesh(obj.data)
            bm_verts_selected = get_selected_bm_vertices(bm, obj)
            bm_verts_island = get_linked_verts(obj, bm, bm_verts_selected)

            if normal and selection_mode == "FACE":
                average_normal = get_average_normal(get_selected_polygons(obj), obj)
                rotation_difference = average_normal.rotation_difference(normal * -1)
                for vert in bm_verts_island:
                    vert.co.rotate(rotation_difference)

            average_location += get_average_location(bm_verts_selected, obj)

            obj_data.append(
                {
                    "object": obj,
                    "selection_indexes": [v.index for v in bm_verts_island],
                }
            )
            bm.free()

        average_location /= len(objs)
        move_offset = average_location - location

        for obj_data_entry in obj_data:
            obj = obj_data_entry["object"]
            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            for i in obj_data_entry["selection_indexes"]:
                location = obj.matrix_world @ bm.verts[i].co.copy()
                location -= move_offset
                bm.verts[i].co = obj.matrix_world.inverted() @ location

            bmesh.update_edit_mesh(obj.data)
            bm.free()
        set_mesh_selection_mode("OBJECT")
        if isinstance(selection_mode, tuple):
            set_mesh_selection_mode(selection_mode[0], selection_mode[1])
        else:
            set_mesh_selection_mode(selection_mode)

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
                difference = (
                    Vector((0.0, 0.0, 1.0)).rotation_difference(normal).to_euler()
                )
                obj.rotation_euler = difference

    def move_to_face(self, context, coords):
        raycast_result, location, normal, _, obj_target = raycast(context, coords)
        if not raycast_result:
            return
        obj_active = context.active_object

        objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]

        if not self.orient:
            normal = None

        if context.mode == "OBJECT":
            self.move_objects_to_point(objs_selected, Vector(location), normal)
        else:
            if len(objs_selected) == 0:
                objs_selected = [obj_active]
            self.move_submeshes_to_point(objs_selected, Vector(location), normal)

        bpy.context.view_layer.objects.active = obj_active
