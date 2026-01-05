from typing import Union

import bpy

from .selection import (
    get_selected_polygons,
    get_mesh_selection_mode,
    set_mesh_selection_mode,
)


def get_materials_on_objects(objs: list[bpy.types.Mesh]) -> list[bpy.types.Material]:
    """Returns a list of all materials linked to the object"""
    materials = []
    for obj in objs:
        for mat in obj.data.materials:
            if mat not in materials and mat != None:
                materials.append(mat)
    return materials


def find_material_id_in_obj(obj: bpy.types.Mesh, material: bpy.types.Material) -> int:
    if not obj.material_slots:
        return -1
    if len(obj.material_slots) > 0:
        material_list = [slot.material for slot in obj.material_slots]
        if material in material_list:
            return material_list.index(material)
    return -1


def get_material_of_polygon(
    obj: bpy.types.Mesh, polygon_index: int
) -> bpy.types.Material:
    """Returns the material of the polygon with given index"""
    material_index = obj.data.polygons[polygon_index].material_index
    max_index = len(obj.material_slots) - 1
    if material_index > max_index:
        material_index = max_index
    return obj.material_slots[material_index].material


def get_polygons_using_material(
    obj: bpy.types.Mesh, material_id: int
) -> list[bpy.types.MeshPolygon]:
    return [p for p in obj.data.polygons if p.material_index == material_id]


def create_new_material(name: str = "Material") -> bpy.types.Material:
    new_name = name
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


def assign_material_id_on_polys(polys: list[bpy.types.MeshPolygon], material_id: int):
    for poly in polys:
        poly.material_index = material_id


def apply_material_on_polys(
    obj: bpy.types.Object,
    polys: Union[list[bpy.types.MeshPolygon], list[int]],
    material: bpy.types.Material,
):
    if isinstance(polys[0], int):
        polys = [obj.data.polygons[i] for i in polys]

    new_mat_index = find_material_id_in_obj(obj, material)
    if new_mat_index == -1:
        obj.data.materials.append(material)
        new_mat_index = len(obj.material_slots) - 1

    assign_material_id_on_polys(polys, new_mat_index)


def apply_material_on_selected_faces(context, material):
    objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
    selection_mode = get_mesh_selection_mode(context)
    set_mesh_selection_mode("OBJECT")

    for obj in objs_selected:
        polys_selected = (
            obj.data.polygons
            if selection_mode == "OBJECT"
            else get_selected_polygons(obj, True)
        )
        apply_material_on_polys(obj, polys_selected, material)

    set_mesh_selection_mode(selection_mode)
