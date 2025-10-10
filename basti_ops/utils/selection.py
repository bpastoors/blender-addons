from typing import Optional, Literal, Union

import bpy
import bmesh

EditMeshSelectionModes: list[Literal["VERT", "EDGE", "FACE"]] = ["VERT", "EDGE", "FACE"]

def mesh_selection_mode(context: bpy.types.Context) -> Union[None, str, tuple[str, tuple]]:
    if context.active_object.mode == "OBJECT":
        return "OBJECT"

    elif context.active_object.mode == "EDIT":
        selection_mask = tuple(context.tool_settings.mesh_select_mode)
        if selection_mask == (True, False, False):
            return "VERT"
        elif selection_mask == (False, True, False):
            return "EDGE"
        elif selection_mask == (False, False, True):
            return "FACE"
        return "MIXED", selection_mask

    return None

def set_mesh_selection_mode(selection_mode: str, selection_mask: Optional[tuple[bool]] = None, curve: Optional[bool] = False):
    if selection_mode == "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
        return

    if curve:
        bpy.ops.object.mode_set(mode="EDIT")
        return

    if selection_mode == "SCULPT":
        bpy.ops.object.mode_set(mode="SCULPT")

    if selection_mode == "MIXED":
        bpy.ops.object.mode_set(mode="EDIT")
        if selection_mask:
            for i in range(0, 3):
                bpy.ops.mesh.select_mode(use_extend=True, type=EditMeshSelectionModes[i], action="ENABLE" if selection_mask[i] is True else "DISABLE")

    if selection_mode in EditMeshSelectionModes:
        bpy.ops.object.mode_set_with_submode(mode="EDIT")
        bpy.ops.mesh.select_mode(type=selection_mode)

def get_continuous_edge_selection(
    edges_selected: list[bmesh.types.BMEdge], start_index: int = 0
) -> (list[bmesh.types.BMEdge], list[bmesh.types.BMEdge]):
    """Returns a continuous edge selection based on the seed index and the rest"""
    edges_connected, edges_connected_to_test = [edges_selected[start_index]]
    edges_selected.remove(edges_selected[start_index])

    while len(edges_connected_to_test) > 0:
        verts_connected = []
        for edge in edges_connected_to_test:
            verts_connected.append(edge.verts[0])
            verts_connected.append(edge.verts[1])
            edges_connected_to_test.remove(edge)
        for edge in edges_selected:
            for vert in edge.verts:
                if vert in verts_connected:
                    edges_connected.append(edge)
                    edges_connected_to_test.append(edge)
                    edges_selected.remove(edge)

    return edges_connected, edges_selected

def get_all_selected_vertices(obj: bpy.types.Mesh, none_is_all: bool = False) -> list[bpy.types.MeshVertex]:
    """Returns a list of selected vertices in the mesh"""
    obj.update_from_editmode()
    selected_vertices = [v for v in obj.data.vertices if v.select]
    if none_is_all and len(selected_vertices) == 0:
        selected_vertices = obj.data.vertices
    return selected_vertices

def get_all_selected_edges(obj: bpy.types.Mesh, none_is_all: bool = False) -> list[bpy.types.MeshEdge]:
    """Returns a list of selected edges in the mesh"""
    obj.update_from_editmode()
    selected_edges = [e for e in obj.data.edges if e.select]
    if none_is_all and len(selected_edges) == 0:
        selected_edges = obj.data.edges
    return selected_edges

def get_all_selected_polygons(
    obj: bpy.types.Object, none_is_all: bool = False
) -> list[bpy.types.MeshPolygon]:
    """Returns a list of selected polygons in the mesh"""
    obj.update_from_editmode()
    selected_polys = [p for p in obj.data.polygons if p.select]
    if none_is_all and len(selected_polys) == 0:
        selected_polys = obj.data.polygons
    return selected_polys

def add_vertices_from_polygons(
    obj_source: bpy.types.Object,
    verts_selected: list[bpy.types.MeshVertex],
    polys_selected: list[bpy.types.MeshPolygon],
) -> list[bpy.types.MeshVertex]:
    """Returns the verts_selected with the vertices of polys_selected added"""
    if len(polys_selected) > 0:
        for p in polys_selected:
            for v_id in p.vertices:
                if obj_source.data.vertices[v_id] not in verts_selected:
                    verts_selected.append(obj_source.data.vertices[v_id])
    return verts_selected

def select_by_id(obj: bpy.types.Object, selection_mode: str, indices: list[int], deselect: bool = False):
    """Selects elements by type and index in the mesh"""
    set_mesh_selection_mode(selection_mode, curve=False)
    if deselect:
        bpy.ops.mesh.select_all(action="DESELECT")
    bm = bmesh.from_edit_mesh(obj.data)

    element_group = None
    if selection_mode == "VERT":
        element_group = bm.verts
    if selection_mode == "EDGE":
        element_group = bm.edges
    if selection_mode == "FACE":
        element_group = bm.faces

    if not element_group:
        raise RuntimeError("No element selected")

    element_group.ensure_lookup_table()

    for i in indices:
        element_group[i].select_set(True)
    bmesh.update_edit_mesh(obj.data)
    bm.free()

def deselect_all(obj: bpy.types.Object):
    """Deselects all elements in the mesh"""




