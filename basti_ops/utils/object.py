from typing import Optional

import bpy

from .selection import (
    get_selected_polygons,
    get_selected_vertices,
    add_vertices_from_polygons,
)


def delete_objects(objs: list[bpy.types.Object]):
    """Deletes a list of objects"""
    with bpy.context.temp_override(selected_objects=objs):
        bpy.ops.object.delete()


def duplicate_object(obj: bpy.types.Object) -> Optional[bpy.types.Object]:
    """Duplicate the object"""
    objs_before = set(bpy.context.scene.objects)
    with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
        bpy.ops.object.duplicate()
    objs_after = set(bpy.context.scene.objects)
    new_objs = list(objs_after - objs_before)
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
