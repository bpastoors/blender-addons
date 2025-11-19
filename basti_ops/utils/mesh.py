from typing import Literal, Union, Optional, Sequence

import bpy
import bmesh
from mathutils import Vector, Quaternion, Euler

from .object import duplicate_object
from .selection import (
    get_mesh_selection_mode,
    get_selected_vertices,
    get_selected_polygons,
    add_vertices_from_polygons,
    set_mesh_selection_mode,
)


def get_all_other_verts(
    bm: bmesh.types.BMesh, verts: list[bmesh.types.BMVert]
) -> list[bmesh.types.BMVert]:
    """Returns a list of all BMVerts in the mesh, but not in the list"""
    return [v for v in bm.verts if v not in verts]


def sort_verts_by_position(
    verts: list[bmesh.types.BMVert],
    sort_by: Literal["X", "Y", "Z"] = "Z",
    descending: bool = False,
) -> list[bmesh.types.BMVert]:
    axis_mapping = {"X": 0, "Y": 1, "Z": 2}
    return sorted(
        verts, key=lambda vert: vert.co[axis_mapping[sort_by]], reverse=descending
    )


def join_meshes(objs: list[bpy.types.Object]) -> bpy.types.Object:
    """Joins a list of Objects into the first one"""
    selection_mode = get_mesh_selection_mode(bpy.context)
    set_mesh_selection_mode("OBJECT")
    if len(objs) < 2:
        return objs[0]
    obj_target = objs[0]
    context_overrides = {
        "object": obj_target,
        "active_object": obj_target,
        "selected_objects": objs,
        "selected_editable_objects": objs,
    }
    with bpy.context.temp_override(**context_overrides):
        bpy.ops.object.join()
        set_mesh_selection_mode(selection_mode)
    return obj_target


def convert_elements_to_verts(
    elements: Union[
        list[bpy.types.MeshVertex],
        list[bmesh.types.BMVert],
        list[bpy.types.MeshEdge],
        list[bmesh.types.BMEdge],
        list[bpy.types.MeshPolygon],
        list[bmesh.types.BMFace],
    ],
    obj: Optional[bpy.types.Object] = None,
) -> Union[list[bpy.types.MeshVertex], list[bmesh.types.BMVert]]:
    if any(
        isinstance(elements[0], vert_type)
        for vert_type in (bpy.types.MeshVertex, bmesh.types.BMVert)
    ):
        return elements

    if any(
        isinstance(elements[0], bm_type)
        for bm_type in (bmesh.types.BMEdge, bmesh.types.BMFace)
    ):
        return [v for e in elements for v in e.verts]

    if not obj:
        raise ValueError("Need object to resolve to vertices, but None was given")

    return [obj.data.vertices[i] for e in elements for i in e.vertices]


def get_average_location(
    elements: Union[
        list[bpy.types.MeshVertex],
        list[bmesh.types.BMVert],
        list[bpy.types.MeshEdge],
        list[bmesh.types.BMEdge],
        list[bpy.types.MeshPolygon],
        list[bmesh.types.BMFace],
    ],
    obj: Optional[bpy.types.Object] = None,
) -> Vector:
    """Return the average vert location"""
    verts = convert_elements_to_verts(elements, obj)

    location = Vector.Fill(3)
    for v in verts:
        location += v.co.copy()
    location /= len(verts)
    return obj.matrix_world @ location if obj else location


def get_average_normal(
    elements: Union[
        list[bpy.types.MeshVertex],
        list[bmesh.types.BMVert],
        list[bpy.types.MeshEdge],
        list[bmesh.types.BMEdge],
        list[bpy.types.MeshPolygon],
        list[bmesh.types.BMFace],
    ],
    obj: Optional[bpy.types.Object] = None,
) -> Vector:
    """Return the average normal"""
    verts = convert_elements_to_verts(elements, obj)

    normal = Vector.Fill(3)
    for v in verts:
        normal += v.normal.copy()
    if obj:
        matrix = obj.matrix_world.to_3x3()
        normal = matrix @ normal
    return normal.normalized()


def copy_selected_into_new_obj(obj: bpy.types.Mesh, cut: bool) -> bpy.types.Mesh:
    """Copies or cuts selected faces of the mesh into a temporary mesh"""
    polys_selected = get_selected_polygons(obj)

    verts_selected_ids = [
        v.index
        for v in add_vertices_from_polygons(
            obj, get_selected_vertices(obj), polys_selected
        )
    ]
    polys_selected_ids = [poly.index for poly in polys_selected]

    obj_target = duplicate_object(obj)
    obj_target_data = obj_target.data
    obj_target.data.name = "mesh"
    obj_target.name = "mesh"

    bm_target = bmesh.new()
    bm_target.from_mesh(obj.data)
    bm_target.verts.ensure_lookup_table()

    verts_keep = [bm_target.verts[index] for index in verts_selected_ids]
    verts_delete = get_all_other_verts(bm_target, verts_keep)

    if polys_selected:
        polys_delete = [
            poly for poly in bm_target.faces if poly.index not in polys_selected_ids
        ]

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


def duplicate_bmesh_geometry(
    bm: bmesh.types.BMesh, verts: list[bmesh.types.BMVert], flip_result: bool = False
) -> list[bmesh.types.BMVert]:
    geom = []
    geom.extend(verts.copy())
    linked_edges = {edge for v in verts for edge in v.link_edges}
    geom.extend({e for e in linked_edges if all(v in verts for v in e.verts)})
    linked_faces = {face for v in verts for face in v.link_faces}
    geom.extend({f for f in linked_faces if all(v in verts for v in f.verts)})

    duplication_result = bmesh.ops.duplicate(bm, geom=geom)
    bm.verts.ensure_lookup_table()
    if flip_result:
        bmesh.ops.reverse_faces(
            bm,
            faces=[
                g
                for g in duplication_result["geom"]
                if isinstance(g, bmesh.types.BMFace)
            ],
        )
    return [g for g in duplication_result["geom"] if isinstance(g, bmesh.types.BMVert)]


def rotate_vertices(
    verts: list[bmesh.types.BMVert],
    rotation: Union[Quaternion, Euler, tuple[Union[Vector, Sequence[float]], float]],
    location_offset: Optional[Vector] = None,
    obj: Optional[bpy.types.Object] = None,
):
    if isinstance(rotation, tuple):
        rotation = Quaternion(*rotation)
    for vert in verts:
        location = vert.co.copy()
        if obj:
            location = obj.matrix_world @ location
        if location_offset:
            location = location - location_offset
        location.rotate(rotation)
        if location_offset:
            location = location + location_offset
        if obj:
            location = obj.matrix_world.inverted() @ location
        vert.co = location
