from typing import Optional, Literal, Union

import bpy
import bmesh


EditMeshSelectionModes: list[Literal["VERT", "EDGE", "FACE"]] = ["VERT", "EDGE", "FACE"]


def mesh_selection_mode(
    context: bpy.types.Context,
) -> Union[None, str, tuple[str, tuple]]:
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


def set_mesh_selection_mode(
    selection_mode: str,
    selection_mask: Optional[tuple[bool, bool, bool]] = None,
    curve: Optional[bool] = False,
):
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
                bpy.ops.mesh.select_mode(
                    use_extend=True,
                    type=EditMeshSelectionModes[i],
                    action="ENABLE" if selection_mask[i] is True else "DISABLE",
                )

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


def get_all_selected(
    obj: bpy.types.Object,
    element_type: Literal["VERT", "EDGE", "FACE"],
    none_is_all: bool = False,
    get_index: bool = False,
):
    obj.update_from_editmode()
    if element_type == "VERT":
        element_group = obj.data.vertices
    elif element_type == "EDGE":
        element_group = obj.data.edges
    elif element_type == "FACE":
        element_group = obj.data.polygons
    else:
        raise RuntimeError("Element group not found")

    selection = [e for e in element_group if e.select]
    if none_is_all and len(selection) == 0:
        selection = element_group
    return [e.index for e in selection] if get_index else selection


def get_all_selected_vertices(
    obj: bpy.types.Object, none_is_all: bool = False, get_index: bool = False
) -> list[bpy.types.MeshVertex]:
    """Returns a list of selected vertices in the mesh"""
    return get_all_selected(obj, "VERT", none_is_all, get_index)


def get_all_selected_edges(
    obj: bpy.types.Object, none_is_all: bool = False, get_index: bool = False
) -> list[bpy.types.MeshEdge]:
    """Returns a list of selected edges in the mesh"""
    return get_all_selected(obj, "EDGE", none_is_all, get_index)


def get_all_selected_polygons(
    obj: bpy.types.Object, none_is_all: bool = False, get_index: bool = False
) -> list[bpy.types.MeshPolygon]:
    """Returns a list of selected polygons in the mesh"""
    return get_all_selected(obj, "FACE", none_is_all, get_index)


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


def get_all_linked_verts(
    obj: bpy.types.Object,
    bm: Optional[bmesh.types.BMesh] = None,
    seed_verts: Optional[
        Union[list[bpy.types.MeshVertex], list[bmesh.types.BMVert], list[int]]
    ] = None,
    get_index: Optional[bool] = False,
) -> Union[list[bpy.types.MeshVertex], list[bmesh.types.BMVert], list[int]]:
    bm_temp = bm or bmesh.from_edit_mesh(obj.data)
    bm_temp.verts.ensure_lookup_table()
    bm_temp.edges.ensure_lookup_table()

    vert_ids = []
    if seed_verts:
        if not isinstance(seed_verts[0], int):
            vert_ids = [v.index for v in seed_verts]
    else:
        vert_ids = get_all_selected_vertices(obj, none_is_all=True, get_index=True)

    checked_edges = []
    edges_to_check = [e for i in vert_ids for e in bm_temp.verts[i].link_edges]

    while len(edges_to_check) > 0:
        edge = edges_to_check.pop()
        checked_edges.append(edge)
        for vert in edge.verts:
            if vert.index in vert_ids:
                continue
            vert_ids.append(vert.index)
            edges_to_check.extend(
                e
                for e in bm_temp.verts[vert.index].link_edges
                if e not in checked_edges
            )

    if not bm:
        bm_temp.free()

    if get_index:
        return vert_ids
    return (
        [bm.verts[i] for i in vert_ids]
        if bm
        else [obj.data.vertices[i] for i in vert_ids]
    )


def get_selected_bm_vertices(
    bm: bmesh.types.BMesh, obj: bpy.types.Object
) -> list[bmesh.types.BMVert]:
    """Returns a list of selected vertices in the mesh"""
    bm.verts.ensure_lookup_table()
    return [bm.verts[i] for i in get_all_selected_vertices(obj, get_index=True)]


def select_by_id(
    obj: bpy.types.Object,
    selection_mode: Literal["VERT", "EDGE", "FACE"],
    indices: list[int],
    clear_selection: bool = True,
    deselect: bool = False,
):
    """Select or deselect elements by type and index in the mesh"""
    set_mesh_selection_mode(selection_mode, curve=False)
    if clear_selection and not deselect:
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
        raise RuntimeError("Element group not found")

    element_group.ensure_lookup_table()

    for i in indices:
        element_group[i].select_set(not deselect)
    bmesh.update_edit_mesh(obj.data)
    bm.free()


def force_deselect_all(obj: bpy.types.Object):
    """Force deselect all elements"""
    obj.select_set(True)
    set_mesh_selection_mode("MIXED", (True, True, True))
    bm = bmesh.from_edit_mesh(obj.data)

    for group in [bm.verts, bm.edges, bm.faces]:
        for element in group:
            element.select_set(False)
    bmesh.update_edit_mesh(obj.data)
    bm.free()


def select_edges_between_vertices(obj: bpy.types.Object):
    obj.update_from_editmode()
    selected_verts = get_all_selected_vertices(obj, get_index=True)
    edges_to_select = [
        e.index for e in obj.data.edges if all(i in selected_verts for i in e.key)
    ]
    select_by_id(obj, "EDGE", edges_to_select)


def select_shared_edges_from_polygons(obj: bpy.types.Object):
    obj.update_from_editmode()
    selected_polys = get_all_selected_polygons(obj)
    if len(selected_polys) < 2:
        raise RuntimeError("Less than two polygons selected")

    all_edge_keys = []
    for poly in selected_polys:
        all_edge_keys.extend(poly.edge_keys)
    shared_keys = [key for key in set(all_edge_keys) if all_edge_keys.count(key) > 1]
    if not shared_keys:
        raise RuntimeError("No shared edges found in polygons")

    selected_edges = get_all_selected_edges(obj)
    shared_edges = [e for e in selected_edges if e.key in shared_keys]
    if not shared_edges:
        raise RuntimeError("Shared edge keys don't match selected edges")

    select_by_id(obj, "EDGE", [e.index for e in shared_edges])


def get_linked_edges(
    obj: bpy.types.Object,
    verts: Union[list[bpy.types.MeshVertex], list[bmesh.types.BMVert]],
) -> Union[list[bpy.types.MeshEdge], list[bmesh.types.BMEdge]]:
    bm = bmesh.from_edit_mesh(obj.data)
    edges = list({edge for vert in verts for edge in bm.verts[vert.index].link_edges})
    bm.free()
    if isinstance(verts[0], bmesh.types.BMVert):
        return edges
    return [obj.data.edges[e.index] for e in edges]


def select_open_border_loop(
    obj: bpy.types.Object,
    selected_edges: Union[list[bpy.types.MeshEdge], list[bmesh.types.BMEdge]],
):
    bm = bmesh.from_edit_mesh(obj.data)
    selected_bm_edges = [
        bm.edges[e.index]
        for e in selected_edges
        if len(bm.edges[e.index].link_faces) == 1
    ]
    neighbours_to_check = [
        linked_edge
        for selected_edge in selected_bm_edges
        for v in selected_edge.verts
        for linked_edge in v.link_edges
        if linked_edge not in selected_bm_edges and len(linked_edge.link_faces) == 1
    ]
    while len(neighbours_to_check) > 0:
        edge = neighbours_to_check[-1]
        neighbours_to_check.remove(edge)
        selected_bm_edges.append(edge)
        neighbours_to_check.extend(
            [
                linked_edge
                for v in edge.verts
                for linked_edge in v.link_edges
                if linked_edge not in selected_bm_edges
                and len(linked_edge.link_faces) == 1
                and linked_edge not in neighbours_to_check
            ]
        )
    bm.free()
    select_by_id(obj, "EDGE", [e.index for e in selected_bm_edges])
