import math

import bpy
import bmesh

from .utils.selection import mesh_selection_mode, deselect_all
from .utils.object import get_evaluated_obj_and_selection, delete_objects
from .utils.mesh import join_meshes, get_all_other_verts
from .utils.raycast import raycast


def copy_selected_into_new_obj(obj: bpy.types.Mesh, cut: bool) -> bpy.types.Mesh:
    """Copies or cuts selected faces of the mesh into a temporary mesh"""
    obj_source, verts_selected, polys_selected = get_evaluated_obj_and_selection(obj)
    verts_selected_ids = [v.index for v in verts_selected]
    polys_selected_ids = [poly.index for poly in polys_selected]

    with bpy.context.temp_override(active_object=obj, selected_objects= [obj]):
        bpy.ops.object.duplicate()
    obj_target = bpy.data.objects[bpy.data.objects.find(obj.name) + 1]
    obj_target_data = obj_target.data
    obj_target.name = "mesh"

    bm_target = bmesh.new()
    bm_target.from_mesh(obj_source.data)
    bm_target.verts.ensure_lookup_table()

    verts_keep = [bm_target.verts[index] for index in verts_selected_ids]
    verts_delete = get_all_other_verts(bm_target, verts_keep)

    if polys_selected:
        polys_delete = [poly for poly in bm_target.faces if poly.index not in polys_selected_ids]

    if cut:
        bm_source = bm_target.copy()
        bm_source.faces.ensure_lookup_table()
        faces_delete = [bm_source.faces[index] for index in polys_selected_ids]
        bmesh.ops.delete(bm_source, geom=faces_delete, context="FACES")
        bm_source.to_mesh(obj.data)
        bm_source.free()

    if polys_selected:
        bmesh.ops.delete(bm_target, geom=polys_delete, context="FACES")
    else:
        bmesh.ops.delete(bm_target, geom=verts_delete)

    bm_target.to_mesh(obj_target_data)
    bm_target.free()

    obj_target.data = obj_target_data
    return obj_target

class BastiCopyToMesh(bpy.types.Operator):
    bl_idname = "basti.copy_to_mesh"
    bl_label = "Copy/Paste polygons into mesh under Cursor"
    bl_options = {"REGISTER", "UNDO"}

    cut: bpy.props.BoolProperty(default=False)

    def copy_cut_to_mesh(self, context, coords, cut=False):
        raycast_result, _, _, _, obj_target = raycast(context, coords)

        bpy.ops.object.mode_set(mode="OBJECT")
        objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
        objs_to_join = []
        for obj in objs_selected:
            objs_to_join.append(copy_selected_into_new_obj(obj, cut))

        if raycast_result and obj_target.type == "MESH":
            deselect_all(obj_target)
            objs_to_join.insert(0, obj_target)

        obj_target = join_meshes(objs_to_join)

        obj_target.select_set(True)
        bpy.context.view_layer.objects.active = obj_target
        bpy.ops.object.mode_set(mode="EDIT")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT'

    def execute(self, context):
        self.copy_cut_to_mesh(context, self.coords, self.cut)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)

def copy_to_clipboard(context, cut=False):
    bpy.ops.object.mode_set(mode="OBJECT")
    obj_active = context.active_object
    objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
    objs_step = []
    for obj in objs_selected:
        objs_step.append(copy_selected_into_new_obj(obj, cut))

    if len(objs_step) > 1:
        obj_copy = join_meshes(objs_step)
    else:
        obj_copy = objs_step[0]

    context = {
        "object": obj_copy,
        "active_object": obj_copy,
        "selected_objects": [obj_copy],
        "selected_editable_objects": [obj_copy],
    }

    with bpy.context.temp_override(**context):
        bpy.ops.view3d.copybuffer()

    delete_objects([obj_copy])

    for obj in objs_selected:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = obj_active
    bpy.ops.object.mode_set(mode="EDIT")

def paste_from_clipboard(context):
    current_mode = context.active_object.mode
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")
    obj_target = context.active_object
    objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]

    bpy.ops.object.select_all(action="DESELECT")

    bpy.ops.view3d.pastebuffer(autoselect=True)
    obj_copy = bpy.context.selected_objects[0]

    if not obj_copy.type == "MESH":
        delete_objects([obj_copy])
    else:
        join_meshes([obj_target, obj_copy])

    for obj in objs_selected:
        obj.select_set(True)
    bpy.ops.object.mode_set(mode=current_mode)

class BastiCopyToClipboard(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.copy_to_clipboard"
    bl_label = "Copy polygons to clipboard"
    bl_options = {"REGISTER", "UNDO"}

    cut: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT'

    def execute(self, context):
        copy_to_clipboard(context, self.cut)
        return {"FINISHED"}

class BastiPasteFromClipboard(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.paste_from_clipboard"
    bl_label = "Paste polygons from clipboard"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        paste_from_clipboard(context)
        return {"FINISHED"}

class BastiRadialArray(bpy.types.Operator):
    """Duplicate selected faces around the cursor"""

    bl_idname = "basti.radial_array"
    bl_label = "Radial Array"
    bl_options = {"REGISTER", "UNDO"}

    pivot: bpy.props.EnumProperty(
        items=[
            ("ORIGIN", "Origin", "World Origin"),
            ("PIVOT", "Pivot", "Object Pivot"),
            ("CURSOR", "Cursor", "3d Cursor"),
        ],
        default="ORIGIN")
    axis: bpy.props.EnumProperty(
        items=[
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z"),
        ],
        default="Z")
    count: bpy.props.IntProperty(default=4)

    @classmethod
    def poll(cls, context):
        return (
                context.active_object is not None
                and context.active_object.type == 'MESH'
                and context.active_object.mode == 'EDIT'
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
        step_objects = []
        bpy.ops.object.mode_set(mode="OBJECT")
        for i in range(1, self.count):
            new_obj = copy_selected_into_new_obj(active_object, False)
            for vert in new_obj.data.vertices:
                coords = bpy.context.object.matrix_world @ Vector(vert.co.copy())
                coords -= rotation_pivot
                coords = coords @ Matrix.Rotation(rotation_rad * i, 4, self.axis)
                coords += rotation_pivot
                vert.co = bpy.context.object.matrix_world.inverted() @ coords
            step_objects.append(new_obj)
        join_meshes([active_object, *step_objects])

        active_object.select_set(True)
        bpy.context.view_layer.objects.active = active_object
        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}

