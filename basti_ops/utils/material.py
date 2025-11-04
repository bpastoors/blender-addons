import bpy

from .selection import get_selected_polygons


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
    material = bpy.data.materials.new(new_name)
    material.use_nodes = True
    return material


def apply_material_on_selected_faces(context, material):
    objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
    context_mode = "OBJECT" if context.mode == "OBJECT" else "EDIT"
    bpy.ops.object.mode_set(mode="OBJECT")

    for obj in objs_selected:
        polys_selected = (
            obj.data.polygons
            if context_mode == "OBJECT"
            else get_selected_polygons(obj, True)
        )

        if len(obj.material_slots) == 0:
            obj.data.materials.append(material)

        material_list = [slot.material for slot in obj.material_slots]
        if material in material_list:
            new_mat_index = material_list.index(material)
        else:
            obj.data.materials.append(material)
            new_mat_index = len(material_list)

        for poly in polys_selected:
            poly.material_index = new_mat_index
    bpy.ops.object.mode_set(mode=context_mode)
