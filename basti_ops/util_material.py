import bpy

from .util_selection import get_all_selected_polygons


def get_materials_on_objects(objs: list[bpy.types.Mesh]) -> list[bpy.types.Material]:
    """Returns a list of all materials linked to the object"""
    materials = []
    for obj in objs:
        for mat in obj.data.materials:
            if mat not in materials and mat != None:
                materials.append(mat)
    return materials


def get_material_of_polygon(
    obj: bpy.types.Mesh, polygon_index: int
) -> bpy.types.Material:
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


def apply_material_on_selected_faces(context, material):
    obj_active = context.active_object

    objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]

    for obj in objs_selected:
        bpy.context.view_layer.objects.active = obj
        if context.mode == "OBJECT":
            polys_selected = obj.data.polygons
            stored_mode = "OBJECT"
        else:
            stored_mode = "EDIT"

        bpy.ops.object.mode_set(mode="OBJECT")
        polys_selected = get_all_selected_polygons(obj, True)

        if len(obj.material_slots) == 0:
            new_mat_index = -1
        else:
            material_list = [slot.material for slot in obj.material_slots]
            try:
                new_mat_index = material_list.index(material)
            except ValueError:
                new_mat_index = -1

        if new_mat_index == -1:
            obj.data.materials.append(new_mat)
            new_mat_index = len(obj.data.materials)

        for poly in polys_selected:
            poly.material_index = new_mat_index
        bpy.ops.object.mode_set(mode=stored_mode)

    bpy.context.view_layer.objects.active = obj_active