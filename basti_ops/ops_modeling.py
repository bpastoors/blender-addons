import bpy
import bmesh
from mathutils import Vector

from .utils.selection import mesh_selection_mode, get_all_selected_vertices
from .utils.mesh import AllLinkedVerts, average_vert_location
from .utils.raycast import raycast


class BastiBevel(bpy.types.Operator):
    """execute right bevel tool based on selection"""

    bl_idname = "basti.bevel"
    bl_label = "Bevel"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
                context.active_object is not None
                and context.active_object.type == 'MESH'
                and context.active_object.mode == 'EDIT'
        )

    def execute(self, context):
        submesh_mode = mesh_selection_mode(context)
        if submesh_mode == "VERT":
            bpy.ops.mesh.bevel("INVOKE_DEFAULT", affect='VERTICES')
        elif submesh_mode == "EDGE":
            bpy.ops.mesh.bevel("INVOKE_DEFAULT",  affect='EDGES')
        elif submesh_mode == "FACE":
            bpy.ops.view3d.edit_mesh_extrude_move_normal()
        return {"FINISHED"}

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
        self.move_to_face(context, self.coords, orient=self.orient)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)

    def move_submeshes_to_point(self, objs: list[bpy.types.Mesh], location: Vector):
        """Move submeshes to the point and rotate them to the normal"""
        obj_data = []
        average_location = Vector((0.0, 0.0, 0.0))
        vertex_count = 0

        for obj in objs:
            verts_selected = get_all_selected_vertices(obj)

            if len(objs) == 1 and len(verts_selected) == 0:
                verts_selected = [obj.data.vertices[-1]]

            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            bm_verts_selected = AllLinkedVerts(
                [bm.verts[v.index] for v in verts_selected]
            ).execute()

            average_location += Vector(average_vert_location(obj, bm_verts_selected))

            obj_data.append({
                "object": obj,
                "selection_indexes": [v.index for v in bm_verts_selected],
            })
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

        for obj in objs:
            average_location += obj.location

        average_location /= len(objs)
        move_offset = average_location - location

        for obj in objs:
            obj.location -= move_offset
            if orient:
                difference = Vector((0.0, 0.0, 1.0)).rotation_difference(normal).to_euler()
                obj.rotation_euler = difference

    def move_to_face(self, context, coords, orient=False):
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

class BastiMergeToActive(bpy.types.Operator):
    """merges all selected vertices at the location of the active vertex"""

    bl_idname = "basti.merge_to_active"
    bl_label = "Merge to Active"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
                context.active_object is not None
                and context.active_object.type == 'MESH'
                and context.active_object.mode == 'EDIT'
                and mesh_selection_mode(context) == "VERT"
        )

    def execute(self, context):
        active_object = context.active_object
        bpy.ops.object.mode_set(mode="OBJECT")
        bm = bmesh.new()
        bm.from_mesh(active_object.data)
        bm.verts.ensure_lookup_table()

        target_vert = bm.select_history.active
        if not target_vert:
            bm.free()
            bpy.ops.object.mode_set(mode="EDIT")
            self.report({"INFO"}, "No active Vertex found to merge to")
            return {"CANCELLED"}
        target_location = target_vert.co.copy()
        selected_verts = get_all_selected_vertices(active_object)

        for i in [vert.index for vert in selected_verts]:
            bm.verts[i].co = target_location

        bm.to_mesh(active_object.data)
        bm.free()
        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.mesh.merge(type='CENTER')

        return {"FINISHED"}

class BastiScaleToZero(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.scale_to_zero"
    bl_label = "Scale to Zero"
    bl_options = {"REGISTER", "UNDO"}

    axis: bpy.props.EnumProperty(
        items=[
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z"),
        ],
        default="X")

    @classmethod
    def poll(cls, context):
        return (
                context.active_object is not None
                and context.active_object.type == 'MESH'
                and context.active_object.mode == 'EDIT'
        )

    def execute(self, context):
        value = (
            0.0 if self.axis == "X" else 1.0,
            0.0 if self.axis == "Y" else 1.0,
            0.0 if self.axis == "Z" else 1.0
        )
        bpy.ops.transform.resize(value=value)
        return {"FINISHED"}

class BastiMoveToZero(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.move_to_zero"
    bl_label = "Move to Zero"
    bl_options = {"REGISTER", "UNDO"}

    x: bpy.props.BoolProperty(name="X", default=True)
    y: bpy.props.BoolProperty(name="Y", default=True)
    z: bpy.props.BoolProperty(name="Z", default=True)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        if context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT':
            verts_selected = get_all_selected_vertices(obj)
            center = average_vert_location(obj, verts_selected)
            value = (
                center[0] * -1.0 if self.x else 0.0,
                center[1] * -1.0 if self.y else 0.0,
                center[2] * -1.0 if self.z else 0.0
            )
            bpy.ops.transform.translate(value=value, orient_type="GLOBAL")
        else:
            new_location = obj.location
            new_location = (
                0.0 if self.x else new_location[0],
                0.0 if self.y else new_location[1],
                0.0 if self.z else new_location[2],
            )
            obj.location = new_location
        return {"FINISHED"}

