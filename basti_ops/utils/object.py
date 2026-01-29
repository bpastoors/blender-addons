from typing import Optional, Literal, Union

import bpy
import bmesh
from mathutils import Vector, Euler, Quaternion

from .selection import (
    get_selected_polygons,
    get_selected_vertices,
    add_vertices_from_polygons,
    select_objects,
    get_mesh_selection_mode,
    set_mesh_selection_mode,
)


def delete_objects(objs: list[bpy.types.Object]):
    """Deletes a list of objects"""
    with bpy.context.temp_override(selected_objects=objs):
        bpy.ops.object.delete()


def duplicate_object(
    obj: bpy.types.Object, instance: bool = False
) -> Optional[bpy.types.Object]:
    """Duplicate the object"""
    selection_mode = get_mesh_selection_mode(bpy.context)
    set_mesh_selection_mode("OBJECT")
    objs_before = set(bpy.context.scene.objects)
    with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
        bpy.ops.object.duplicate(linked=instance)
    objs_after = set(bpy.context.scene.objects)
    new_objs = list(objs_after - objs_before)
    set_mesh_selection_mode(selection_mode)
    return new_objs[0] if new_objs else None


def get_evaluated_obj_and_selection(
    obj: bpy.types.Object,
) -> tuple[bpy.types.Object, list[bpy.types.MeshVertex], list[bpy.types.MeshPolygon]]:
    """Sets the object active and returns the evaluated object and the selected vertices and polygons"""

    bpy.context.view_layer.objects.active = obj
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_evaluated = obj.evaluated_get(depsgraph)
    polys_selected = get_selected_polygons(obj_evaluated)
    verts_selected = get_selected_vertices(obj_evaluated)

    verts_selected = add_vertices_from_polygons(
        obj_evaluated, verts_selected, polys_selected
    )
    return obj_evaluated, verts_selected, polys_selected


def align_euler_axis_with_direction(
    obj, axis: Union[int, Literal["x", "y", "z"]], direction: Vector
) -> Quaternion:
    if not isinstance(axis, int):
        if axis == "x":
            axis = 0
        elif axis == "y":
            axis = 1
        elif axis == "z":
            axis = 2
    axis_vector = Vector.Fill(3)
    axis_vector[axis] = 1.0

    obj_matrix = obj.rotation_euler.to_matrix()
    obj_axis = obj_matrix @ axis_vector
    rotation_diff = obj_axis.rotation_difference(direction.normalized())
    obj.rotation_euler = (rotation_diff.to_matrix() @ obj_matrix).to_euler()
    return rotation_diff


def add_new_mesh_object(
    name: str,
    select: bool = True,
    set_active: bool = True,
    next_to_obj: Optional[bpy.types.Object] = None,
    collections: Optional[list[bpy.types.Collection]] = None,
) -> bpy.types.Object:
    """Add a new mesh object to the collections or in the collection the next_to_obj is in"""
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    target_collections = set()

    if collections:
        target_collections.update(collections)

    if next_to_obj:
        target_collections.update(
            {c for c in bpy.data.collections if next_to_obj.name in c.objects}
        )

    if not target_collections:
        target_collections = {bpy.context.scene.collection}

    for col in target_collections:
        col.objects.link(obj)

    if select or set_active:
        select_objects([obj], set_active=set_active)
    return obj


def get_average_object_location(objs: list[bpy.types.Object]) -> Vector:
    average_location = Vector((0.0, 0.0, 0.0))
    for obj in objs:
        average_location += obj.location
    return average_location / len(objs)


def get_average_object_rotation_euler(objs: list[bpy.types.Object]) -> Vector:
    average_rotation = Vector((0.0, 0.0, 0.0))
    for obj in objs:
        average_rotation += Vector([*obj.rotation_euler])
    return average_rotation / len(objs)


def set_object_location(
    obj: bpy.types.Object, location: Vector, compensate: bool = True
):
    selection_mode = get_mesh_selection_mode(bpy.context)
    if compensate:
        set_mesh_selection_mode("OBJECT")
        location_offset = location - obj.location
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            coords = obj.matrix_world @ vert.co.copy()
            coords -= location_offset
            vert.co = obj.matrix_world.inverted() @ coords
        bm.to_mesh(obj.data)
        bm.free()
    obj.location = location
    set_mesh_selection_mode(selection_mode)


def set_object_rotation_euler(
    obj: bpy.types.Object, rotation: Euler, compensate: bool = True
):
    selection_mode = get_mesh_selection_mode(bpy.context)
    if compensate:
        set_mesh_selection_mode("OBJECT")
        rotation_quat = rotation.to_quaternion()
        rotation_offset = rotation_quat.rotation_difference(
            obj.rotation_euler.to_quaternion()
        )
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            coords = vert.co.copy()
            coords.rotate(rotation_offset)
            vert.co = coords
        bm.to_mesh(obj.data)
        bm.free()
    obj.rotation_euler = rotation
    set_mesh_selection_mode(selection_mode)
