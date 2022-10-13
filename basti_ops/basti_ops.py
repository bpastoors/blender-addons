import bpy
import bmesh
from mathutils import Vector


def get_all_selected_polygons(obj: bpy.types.Mesh, none_is_all: bool = False) -> list[bpy.types.MeshPolygon]:
    """Returns a list of selected polygons in the mesh"""
    selected_polys = [p for p in obj.data.polygons if p.select]
    if none_is_all and len(selected_polys) == 0:
        selected_polys = obj.data.polygons
    return selected_polys


def get_all_selected_vertices(obj: bpy.types.Mesh) -> list[bpy.types.MeshVertex]:
    """Returns a list of selected vertices in the mesh"""
    return [v for v in obj.data.vertices if v.select]


def add_vertices_from_polygons(obj_source: bpy.types.Mesh, verts_selected: list[bpy.types.MeshVertex], polys_selected: list[bpy.types.MeshPolygon]) -> list[bpy.types.MeshVertex]: 
    """Returns the verts_selected with the vertices of polys_selected added"""
    if len(polys_selected) > 0:
        for p in polys_selected:
            for v_id in p.vertices:
                if obj_source.data.vertices[v_id] not in verts_selected:
                    verts_selected.append(obj_source.data.vertices[v_id])
    return verts_selected

def get_source_obj_and_selection(obj: bpy.types.Object) -> tuple[bpy.types.Object, list[bpy.types.MeshVertex], list[bpy.types.MeshPolygon]]:
    """Sets the object active and returns the evaluated object and the selected vertices and polygons"""
    bpy.context.view_layer.objects.active = obj
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_source = obj.evaluated_get(depsgraph)
    polys_selected = get_all_selected_polygons(obj_source)
    verts_selected = get_all_selected_vertices(obj_source)

    verts_selected = add_vertices_from_polygons(obj_source, verts_selected, polys_selected)
    return obj_source, verts_selected, polys_selected


def get_all_other_verts(bm: bmesh, verts: list[bmesh.types.BMVert]) -> list[bmesh.types.BMVert]:
    """Returns a list of all BMVerts in the mesh, but not in the list"""
    return [v for v in bm.verts if v not in verts]


def join_meshes(objs: list[bpy.types.Mesh]) -> bpy.types.Mesh:
    """Joins a list of Objects into the first one"""
    context = {}
    context["object"] = context["active_object"] = objs[0]
    context["selected_objects"] = context["selected_editable_objects"] = objs
    bpy.ops.object.join(context)
    return objs[0]


def delete_objects(objs:list[bpy.types.Object]):
    """Deletes a list of objects"""
    bpy.ops.object.delete({'selected_objects': objs})


def copy_into_step_obj(obj: bpy.types.Mesh, cut: bool) -> bpy.types.Mesh:
    """Copies or cuts selected faces of the mesh into a temporary mesh"""
    obj_source, verts_selected, polys_selected = get_source_obj_and_selection(obj)

    vert_locations = [bpy.context.object.matrix_world @ obj_source.data.vertices[v.index].co.copy() for v in verts_selected]

    bm_target = bmesh.new()
    bm_target.from_mesh(obj_source.data)
    bm_target.verts.ensure_lookup_table()

    verts_keep = [bm_target.verts[v.index] for v in verts_selected]
    verts_delete = get_all_other_verts(bm_target, verts_keep)

    if cut:
        bm_source = bm_target.copy()
        bm_source.faces.ensure_lookup_table()
        faces_delete = [bm_source.faces[p.index] for p in polys_selected]
        bmesh.ops.delete(bm_source, geom=faces_delete, context='FACES')
        bm_source.to_mesh(obj.data)
        bm_source.free()

    bmesh.ops.delete(bm_target, geom=verts_delete)

    for v in verts_keep:
        v.co = vert_locations[v.index]

    obj_step_data = bpy.data.meshes.new("meshdata")
    bm_target.to_mesh(obj_step_data)
    obj_step = bpy.data.objects.new("mesh", obj_step_data)

    bm_target.free()
    return obj_step


def raycast(context, coords) -> tuple[bool, list[float], list[float], int, bpy.types.Object]:
    """Casts a ray at the mouse position and returns raycast_result, location, normal, face_index, obj_target"""
    from bpy_extras import view3d_utils
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    depsgraph = bpy.context.evaluated_depsgraph_get()

    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coords)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coords)

    raycast_result, location, normal, polygon_index, obj_target, _ = scene.ray_cast(depsgraph, ray_origin, view_vector)
    return raycast_result, location, normal, polygon_index, obj_target


def copy_cut_to_mesh(context, coords, cut=False):
    raycast_result, _, _, _, obj_target = raycast(context, coords)

    bpy.ops.object.mode_set(mode='OBJECT')
    objs_selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
    objs_step = []
    for obj in objs_selected:
        objs_step.append(copy_into_step_obj(obj, cut))

    if raycast_result and obj_target.type == 'MESH':
        objs_merge = [obj_target]
        objs_merge.extend(objs_step)
        join_meshes(objs_merge)
    else:
        obj_target = join_meshes(objs_step)
        objs_selected[0].users_collection[0].objects.link(obj_target)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj_target
    obj_target.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')


class BastiCopyToMesh(bpy.types.Operator):
    bl_idname = "basti.copy_to_mesh"
    bl_label = "Copy/Paste polygons into mesh under Cursor"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        copy_cut_to_mesh(context, self.coords)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)


class BastiCutToMesh(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "basti.cut_to_mesh"
    bl_label = "Cut/Paste polygons into mesh under Cursor"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        copy_cut_to_mesh(context, self.coords, True)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)


def copy_to_clipboard(context, cut=False):
    bpy.ops.object.mode_set(mode='OBJECT')
    objs_selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
    objs_step = []
    for obj in objs_selected:
        objs_step.append(copy_into_step_obj(obj, cut))
    
    if len(objs_step) > 1:
        obj_copy = join_meshes(objs_step)
    else:
        obj_copy = objs_step[0]
    objs_selected[0].users_collection[0].objects.link(obj_copy)
    
    context = {}
    context["object"] = context["active_object"] = obj_copy
    context["selected_objects"] = context["selected_editable_objects"] = [obj_copy]
    bpy.ops.object.select_all(action='DESELECT')
    obj_copy.select_set(True)

    bpy.ops.view3d.copybuffer(context)

    delete_objects([obj_copy])

    for obj in objs_selected:
        obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')


def paste_from_clipboard(context):
    bpy.ops.object.mode_set(mode='OBJECT')
    obj_target = context.active_object
    
    bpy.ops.view3d.pastebuffer()
    obj_copy = bpy.data.objects[len(bpy.data.objects) - 1]
    
    context_target = {"object": obj_target, "active_object": obj_target,
    "selected_objects": [obj_target], "selected_editable_objects": [obj_target], "mode": "EDIT_MESH"}
    context_copy = {"object": obj_copy, "active_object": obj_copy,
    "selected_objects": [obj_copy], "selected_editable_objects": [obj_copy], "mode": "EDIT_MESH"}
    
    # bpy.ops.object.mode_set({"active_object": obj_target}, mode='EDIT')
    bpy.ops.mesh.select_all(context_target, action='SELECT')
    bpy.ops.mesh.select_all(context_copy, action='DESELECT')
    # bpy.ops.object.mode_set({"active_object": obj_target}, mode='OBJECT')

    # bpy.ops.object.select_all(action='DESELECT')
    # obj_target.select_set(True)
    # bpy.context.view_layer.objects.active = obj_target
    return
    bpy.ops.object.mode_set({"active_object": obj_copy},mode='EDIT')
    bpy.ops.mesh.select_all({"active_object": obj_copy, "selected_editable_objects": [obj_copy]}, action='SELECT')
    bpy.ops.object.mode_set({"active_object": obj_copy}, mode='OBJECT')
    to_join = [obj_target, obj_copy]
    obj_target = join_meshes(to_join)

    bpy.ops.object.select_all(action='DESELECT')
    obj_target.select_set(True)
    bpy.context.view_layer.objects.active = obj_target
    bpy.ops.object.mode_set(mode='EDIT')


class BastiCopyToClipboard(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "basti.copy_to_clipboard"
    bl_label = "Copy polygons to clipboard"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        copy_to_clipboard(context)
        return {'FINISHED'}


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
        return {'FINISHED'}


class AllLinkedVerts():
    """recursively finds all bmesh verts in the submesh and adds them to vertsLinked list"""
    def __init__(self, vertsLinked: list[bmesh.types.BMVert]):
        self.checkedFaces = []
        self.vertsLinked = vertsLinked
        for v in self.vertsLinked:
            self.RecursiveSearch(v)

    def RecursiveSearch(self, seedVert: bmesh.types.BMVert):
        """Finds all BMVerts link to the seed vert"""
        newVerts = []
        for f in seedVert.link_faces:
            if f in self.checkedFaces:
                continue

            self.checkedFaces.append(f)
            for v in f.verts:
                if v in self.vertsLinked:
                    continue

                self.vertsLinked.append(v)
                newVerts.append(v)

        if len(newVerts) > 0:
            for v in newVerts:
                self.RecursiveSearch(v)


def move_submeshes_to_point(objs: list[bpy.types.Mesh], location: Vector):
    """Move submeshes to the point and rotate them to the normal"""
    obj_data = []
    average_location = Vector((0.0, 0.0, 0.0))
    vertex_count = 0

    for obj in objs:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT')

        obj_source, verts_selected, polys_selected = get_source_obj_and_selection(obj)

        if len(objs) == 1 and len(verts_selected) == 0:
            verts_selected = [obj_source.data.vertices[-1]]

        bm = bmesh.new()
        bm.from_mesh(obj_source.data)
        bm.verts.ensure_lookup_table()
        bm_verts_selected = AllLinkedVerts([bm.verts[v.index] for v in verts_selected]).vertsLinked

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
        bpy.ops.object.mode_set(mode='OBJECT')

        bm = obj_data_entry["bmesh"]
        bm.verts.ensure_lookup_table()
        verts = [bm.verts[i] for i in obj_data_entry["selectionIndexes"]]

        for v in verts:
            v.co -= move_offset

        bm.to_mesh(obj_data_entry["object"].data)
        bm.free()
        bpy.ops.object.mode_set(mode='EDIT')


def move_objects_to_point(objs: list[bpy.types.Object], location: Vector, orient: bool = False, normal: Vector = Vector((0.0, 0.0, 0.0))):
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


def move_to_face(context, coords, orient=False):
    raycast_result, location, normal, _, obj_target = raycast(context, coords)
    if not raycast_result:
        return
    obj_active = context.active_object

    objs_selected = [obj for obj in context.selected_objects if obj.type == 'MESH']

    if context.mode == "OBJECT":
        move_objects_to_point(objs_selected, location, orient, normal)
    else:
        move_submeshes_to_point(objs_selected, location)

    bpy.context.view_layer.objects.active = obj_active


class BastiMoveToFace(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "basti.move_to_face"
    bl_label = "move selected submesh or object to face under Cursor"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        move_to_face(context, self.coords)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)


class BastiMoveAndOrientToFace(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "basti.move_and_orient_to_face"
    bl_label = "move selected submesh or object to face under Cursor and orient to the normal"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        move_to_face(context, self.coords, True)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)


def get_materials_on_objects(objs: list[bpy.types.Mesh]) -> list[bpy.types.Material]:
    """Returns a list of all materials linked to the object"""
    materials = []
    for obj in objs:
        for mat in obj.data.materials:
            if mat not in materials and mat != None:
                materials.append(mat)
    return materials


def get_material_of_polygon(obj: bpy.types.Mesh, polygon_index: int) -> bpy.types.Material:
    """Returns the material of the polygon with given index"""
    material_index = obj.data.polygons[polygon_index].material_index
    max_index = len(obj.material_slots) - 1
    if material_index > max_index:
        material_index = max_index
    return obj.material_slots[material_index].material


def create_new_material():
    new_name = "Material"
    material_found = False
    count_up = 1
    if bpy.data.materials.find(new_name):
        material_found = True
    while material_found:
        find_name = new_name + "." + str(count_up).zfill(3)
        if bpy.data.materials.find(find_name) == -1:
            material_found = False
            new_name = find_name
    return bpy.data.materials.new(new_name)


def apply_material(context, coords):
    raycast_result, _, _, polygon_index, obj_target = raycast(context, coords)
    obj_active = context.active_object
    
    if not raycast_result:
        new_mat = create_new_material()
    else:
        new_mat = get_material_of_polygon(obj_target, polygon_index)

    objs_selected = [obj for obj in context.selected_objects if obj.type == 'MESH']

    for obj in objs_selected:
        bpy.context.view_layer.objects.active = obj
        if context.mode == "OBJECT":
            polys_selected = obj.data.polygons
            stored_mode = "OBJECT"
        else:
            stored_mode = "EDIT"

        bpy.ops.object.mode_set(mode='OBJECT')
        polys_selected = get_all_selected_polygons(obj, True)

        if len(obj.material_slots) == 0:
           new_mat_index = -1
        else:
            material_list = [slot.material for slot in obj.material_slots]
            try:
                new_mat_index = material_list.index(new_mat)
            except ValueError:
                new_mat_index = -1

        if new_mat_index == -1:
            obj.data.materials.append(new_mat)
            new_mat_index = len(obj.data.materials)

        for poly in polys_selected:
            poly.material_index = new_mat_index
        bpy.ops.object.mode_set(mode=stored_mode)

    bpy.context.view_layer.objects.active = obj_active


class BastiApplyMaterial(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "basti.apply_material"
    bl_label = "apply material under cursor to selected polygons"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        apply_material(context, self.coords)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)


# class TraceSpriteToMesh(bpy.types.Operator):
#     bl_idname = "basti.trace_sprite"
#     bl_label = "Create a mesh based on the sprite"

#     @classmethod
#     def poll(cls, context):
#         return True

#     def execute(self, context):
#         image = bpy.data.images["FOX_head.png"]

#         image_size = image.size
#         pixels = list(image.pixels)
#         pixels_len = len(pixels)

#         pixel_alphas = [pixels[i] for i in range(3, pixels_len, 4)]

#         print(len(pixel_alphas))
#         print(image_size[0] * image_size[1])
#         return {'FINISHED'}


class PlanarUV01(bpy.types.Operator):
    bl_idname = "basti.planar_uv_01"
    bl_label = "Planar uvs with set size"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        mesh = bpy.context.active_object
        mesh.data.uv_layers.new(name='spriteUV', do_init=False)

        bm = bmesh.new()
        bm.from_mesh(mesh.data)
        uv_layer = bm.loops.layers.uv['spriteUV']
        for vert in bm.verts:
            for loop in vert.link_loops:
                luv = loop[uv_layer]
                coords = vert.co.copy()
                luv.uv = (coords[0] + 0.5, coords[1] + 0.5)
        bm.to_mesh(mesh.data)
        bm.free()

        return {'FINISHED'}


classes = [
    BastiCopyToMesh,
    BastiCutToMesh,
    BastiCopyToClipboard,
    BastiPasteFromClipboard,
    BastiMoveToFace,
    BastiMoveAndOrientToFace,
    BastiApplyMaterial,
    # TraceSpriteToMesh,
    PlanarUV01
    ]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
