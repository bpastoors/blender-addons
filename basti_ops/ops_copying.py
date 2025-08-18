import bpy
import bmesh

def copy_selected_into_new_obj(obj: bpy.types.Mesh, cut: bool) -> bpy.types.Mesh:
    """Copies or cuts selected faces of the mesh into a temporary mesh"""
    from util_object import get_evaluated_obj_and_selection
    from util_mesh import get_all_other_verts

    obj_source, verts_selected, polys_selected = get_evaluated_obj_and_selection(obj)

    vert_locations = [
        bpy.context.object.matrix_world @ obj_source.data.vertices[v.index].co.copy()
        for v in verts_selected
    ]

    bm_target = bmesh.new()
    bm_target.from_mesh(obj_source.data)
    bm_target.verts.ensure_lookup_table()

    verts_keep = [bm_target.verts[v.index] for v in verts_selected]
    verts_delete = get_all_other_verts(bm_target, verts_keep)

    if polys_selected:
        polys_selected_ids = [poly.index for poly in polys_selected]
        polys_delete = [poly for poly in bm_target.faces if poly.index not in polys_selected_ids]

    if cut:
        bm_source = bm_target.copy()
        bm_source.faces.ensure_lookup_table()
        faces_delete = [bm_source.faces[p.index] for p in polys_selected]
        bmesh.ops.delete(bm_source, geom=faces_delete, context="FACES")
        bm_source.to_mesh(obj.data)
        bm_source.free()

    for v in verts_keep:
        v.co = vert_locations[v.index]

    if polys_selected:
        bmesh.ops.delete(bm_target, geom=polys_delete, context="FACES")
    else:
        bmesh.ops.delete(bm_target, geom=verts_delete)

    obj_step_data = bpy.data.meshes.new("meshdata")
    bm_target.to_mesh(obj_step_data)
    bm_target.free()
    return bpy.data.objects.new("mesh", obj_step_data)

class BastiCopyToMesh(bpy.types.Operator):
    bl_idname = "basti.copy_to_mesh"
    bl_label = "Copy/Paste polygons into mesh under Cursor"
    bl_options = {"REGISTER", "UNDO"}

    cut: bpy.props.BoolProperty(default=False)

    def copy_cut_to_mesh(self, context, coords, cut=False):
        from util_raycast import raycast
        from util_mesh import join_meshes

        raycast_result, _, _, _, obj_target = raycast(context, coords)

        bpy.ops.object.mode_set(mode="OBJECT")
        objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
        objs_step = []
        for obj in objs_selected:
            objs_step.append(self.copy_selected_into_new_obj(obj, cut))

        if raycast_result and obj_target.type == "MESH":
            objs_merge = [obj_target]
            objs_merge.extend(objs_step)
            join_meshes(objs_merge)
        else:
            obj_target = join_meshes(objs_step)
            objs_selected[0].users_collection[0].objects.link(obj_target)

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj_target
        obj_target.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        self.copy_cut_to_mesh(context, self.coords, self.cut)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)

def copy_to_clipboard(context, cut=False):
    from util_mesh import join_meshes
    from util_object import delete_objects

    bpy.ops.object.mode_set(mode="OBJECT")
    objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
    objs_step = []
    for obj in objs_selected:
        objs_step.append(copy_selected_into_new_obj(obj, cut))

    if len(objs_step) > 1:
        obj_copy = join_meshes(objs_step)
    else:
        obj_copy = objs_step[0]
    objs_selected[0].users_collection[0].objects.link(obj_copy)

    context = {}
    context["object"] = context["active_object"] = obj_copy
    context["selected_objects"] = context["selected_editable_objects"] = [obj_copy]
    bpy.ops.object.select_all(action="DESELECT")
    obj_copy.select_set(True)

    with bpy.context.temp_override(**context):
        bpy.ops.view3d.copybuffer()

    delete_objects([obj_copy])

    for obj in objs_selected:
        obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")

def paste_from_clipboard(context):
    bpy.ops.object.mode_set(mode="OBJECT")
    obj_target = context.active_object

    bpy.ops.view3d.pastebuffer()
    obj_copy = bpy.data.objects[len(bpy.data.objects) - 1]

    context_target = {
        "object": obj_target,
        "active_object": obj_target,
        "selected_objects": [obj_target],
        "selected_editable_objects": [obj_target],
        "mode": "EDIT_MESH",
    }
    context_copy = {
        "object": obj_copy,
        "active_object": obj_copy,
        "selected_objects": [obj_copy],
        "selected_editable_objects": [obj_copy],
        "mode": "EDIT_MESH",
    }

    # bpy.ops.object.mode_set({"active_object": obj_target}, mode='EDIT')
    with bpy.context.temp_override(**context_target):
        bpy.ops.mesh.select_all(action="SELECT")
    with bpy.context.temp_override(**context_copy):
        bpy.ops.mesh.select_all(action="DESELECT")
    # bpy.ops.object.mode_set({"active_object": obj_target}, mode='OBJECT')

    # bpy.ops.object.select_all(action='DESELECT')
    # obj_target.select_set(True)
    # bpy.context.view_layer.objects.active = obj_target
    return
    bpy.ops.object.mode_set({"active_object": obj_copy}, mode="EDIT")
    bpy.ops.mesh.select_all(
        {"active_object": obj_copy, "selected_editable_objects": [obj_copy]},
        action="SELECT",
    )
    bpy.ops.object.mode_set({"active_object": obj_copy}, mode="OBJECT")
    to_join = [obj_target, obj_copy]
    obj_target = join_meshes(to_join)

    bpy.ops.object.select_all(action="DESELECT")
    obj_target.select_set(True)
    bpy.context.view_layer.objects.active = obj_target
    bpy.ops.object.mode_set(mode="EDIT")

class BastiCopyToClipboard(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.copy_to_clipboard"
    bl_label = "Copy polygons to clipboard"
    bl_options = {"REGISTER", "UNDO"}

    cut: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

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