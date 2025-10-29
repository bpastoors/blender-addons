from typing import Literal

import bpy
import bmesh

from .object import duplicate_object
from .selection import (
    mesh_selection_mode,
    get_all_selected_vertices,
    get_all_selected_polygons,
    add_vertices_from_polygons,
    set_mesh_selection_mode,
)


class AllLinkedVerts:
    """recursively finds all bmesh verts in the submesh and adds them to vertsLinked list"""

    def __init__(self, seed_verts: list[bmesh.types.BMVert]):
        self.checked_faces = []
        self.verts_linked = seed_verts
        self.seed_verts = seed_verts

    def execute(self):
        for vert in self.seed_verts:
            self.recursive_search(vert)
        return self.verts_linked

    def recursive_search(self, seed_vert: bmesh.types.BMVert):
        """Finds all BMVerts link to the seed vert"""
        new_verts = []
        for f in seed_vert.link_faces:
            if f in self.checked_faces:
                continue

            self.checked_faces.append(f)
            for v in f.verts:
                if v in self.verts_linked:
                    continue

                self.verts_linked.append(v)
                new_verts.append(v)

        if len(new_verts) > 0:
            for v in new_verts:
                self.recursive_search(v)


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
    selection_mode = mesh_selection_mode(bpy.context)
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


def average_vert_location(
    obj: bpy.types.Object, verts: list[bpy.types.MeshVertex]
) -> tuple[float, float, float]:
    """Return the average vert location"""
    vert_locations = [obj.matrix_world @ v.co.copy() for v in verts]
    x, y, z = (0.0, 0.0, 0.0)
    for location in vert_locations:
        x += location[0]
        y += location[1]
        z += location[2]
    return x / len(verts), y / len(verts), z / len(verts)


def copy_selected_into_new_obj(obj: bpy.types.Mesh, cut: bool) -> bpy.types.Mesh:
    """Copies or cuts selected faces of the mesh into a temporary mesh"""
    polys_selected = get_all_selected_polygons(obj)

    verts_selected_ids = [
        v.index
        for v in add_vertices_from_polygons(
            obj, get_all_selected_vertices(obj), polys_selected
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
