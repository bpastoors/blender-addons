import bpy
import bmesh
from mathutils import Vector


class BastiMoveToFace(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.move_to_face"
    bl_label = "move selected submesh or object to face under Cursor"
    bl_options = {"REGISTER", "UNDO"}

    orient: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        self.move_to_face(context, self.coords, orient=self.orient)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)

    def move_submeshes_to_point(self, objs: list[bpy.types.Mesh], location: Vector):
        """Move submeshes to the point and rotate them to the normal"""
        from util_object import get_evaluated_obj_and_selection
        from util_mesh import AllLinkedVerts

        obj_data = []
        average_location = Vector((0.0, 0.0, 0.0))
        vertex_count = 0

        for obj in objs:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode="OBJECT")

            obj_source, verts_selected, polys_selected = get_evaluated_obj_and_selection(obj)

            if len(objs) == 1 and len(verts_selected) == 0:
                verts_selected = [obj_source.data.vertices[-1]]

            bm = bmesh.new()
            bm.from_mesh(obj_source.data)
            bm.verts.ensure_lookup_table()
            bm_verts_selected = AllLinkedVerts(
                [bm.verts[v.index] for v in verts_selected]
            ).execute()

            for v in bm_verts_selected:
                average_location += bpy.context.object.matrix_world @ v.co.copy()
            vertex_count += len(bm_verts_selected)

            obj_data_entry = {}
            obj_data_entry["object"] = obj
            obj_data_entry["selectionIndexes"] = [v.index for v in bm_verts_selected]
            obj_data_entry["bmesh"] = bm.copy()
            obj_data.append(obj_data_entry)

            bm.free()

        average_location /= vertex_count
        move_offset = average_location - location

        for obj_data_entry in obj_data:
            bpy.context.view_layer.objects.active = obj_data_entry["object"]
            bpy.ops.object.mode_set(mode="OBJECT")

            bm = obj_data_entry["bmesh"]
            bm.verts.ensure_lookup_table()
            verts = [bm.verts[i] for i in obj_data_entry["selectionIndexes"]]

            for v in verts:
                v.co -= move_offset

            bm.to_mesh(obj_data_entry["object"].data)
            bm.free()
            bpy.ops.object.mode_set(mode="EDIT")

    def move_objects_to_point(
            self,
            objs: list[bpy.types.Object],
            location: Vector,
            orient: bool = False,
            normal: Vector = Vector((0.0, 0.0, 0.0)),
    ):
        """Move and orient meshes to the point and rotate them to the normal"""
        average_location = Vector((0.0, 0.0, 0.0))
        object_count = 0

        for obj in objs:
            average_location += obj.location
            object_count += 1

        average_location /= object_count
        move_offset = average_location - location

        for obj in objs:
            obj.location -= move_offset
            if orient:
                difference = Vector((0.0, 0.0, 1.0)).rotation_difference(normal).to_euler()
                obj.rotation_euler = difference

    def move_to_face(self, context, coords, orient=False):
        from util_raycast import raycast

        raycast_result, location, normal, _, obj_target = raycast(context, coords)
        if not raycast_result:
            return
        obj_active = context.active_object

        objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]

        if context.mode == "OBJECT":
            self.move_objects_to_point(objs_selected, Vector(location), orient, normal)
        else:
            self.move_submeshes_to_point(objs_selected, Vector(location))

        bpy.context.view_layer.objects.active = obj_active