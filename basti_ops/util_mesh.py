from typing import Literal

import bpy
import bmesh


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
        bm: bmesh, verts: list[bmesh.types.BMVert]
) -> list[bmesh.types.BMVert]:
    """Returns a list of all BMVerts in the mesh, but not in the list"""
    return [v for v in bm.verts if v not in verts]

def sort_verts_by_position(verts: list[bmesh.types.BMVert], sort_by: Literal["X", "Y", "Z"] = "Z", descending: bool = False) -> list[bmesh.types.BMVert]:
    axis_mapping = {"X": 0, "Y": 1, "Z": 2}
    return sorted(verts, key=lambda vert: vert.co[axis_mapping[sort_by]], reverse=descending)

def join_meshes(objs: list[bpy.types.Mesh]) -> bpy.types.Mesh:
    """Joins a list of Objects into the first one"""
    context_overrides = {
        "object": objs[0],
        "active_object": objs[0],
        "selected_objects": objs,
        "selected_editable_objects": objs
    }
    with bpy.context.temp_override(**context_overrides):
        bpy.ops.object.join()
    return objs[0]



