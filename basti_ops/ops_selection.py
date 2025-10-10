import bpy, bmesh

from .utils.selection import select_by_id, set_mesh_selection_mode, mesh_selection_mode, get_all_selected_polygons, get_all_selected_edges


class BastiSetSelectionMode(bpy.types.Operator):
    bl_idname = "basti.set_selection_mode"
    bl_label = "Set Mesh Selection Mode"
    bl_options = {"REGISTER", "UNDO"}

    selection_mode: bpy.props.EnumProperty(
        items=[
            ("VERT", "VERT", "Vertex"),
            ("EDGE", "EDGE", "Edge"),
            ("FACE", "FACE", "Face"),
            ("OBJECT", "OBJECT", "Object"),
            ("SCULPT", "SCULPT", "Sculpt"),
        ],
        default="OBJECT")

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        return context.active_object.type == 'CURVE' or context.active_object.type == 'MESH'

    def execute(self, context):
        set_mesh_selection_mode(self.selection_mode, curve=context.active_object.type == 'CURVE')
        return {"FINISHED"}

class BastiSelectEdgeOrIsland(bpy.types.Operator):
    bl_idname = "basti.select_edge_or_island"
    bl_label = "Select Edge Loop or Island"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        return context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT'

    def execute(self, context):
        selection_mode = mesh_selection_mode(context)
        if selection_mode == "EDGE":
            bpy.ops.mesh.loop_multi_select(ring=False)
        if selection_mode in ["FACE", "VERT"]:
            bpy.ops.mesh.select_linked()
        return {"FINISHED"}


class BastiSelectLoop(bpy.types.Operator):
    bl_idname = "basti.select_loop"
    bl_label = "Select Edge Loop or Face Loop"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        return context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT'

    def execute(self, context):
        selection_mode = mesh_selection_mode(context)
        if not selection_mode in ["VERT", "EDGE", "FACE"]:
            return {"FINISHED"}

        if selection_mode in ["VERT", "EDGE"]:
            bpy.ops.mesh.loop_multi_select(ring=False)
            return {"FINISHED"}

        obj = context.active_object
        obj.update_from_editmode()
        selected_polys = get_all_selected_polygons(obj)
        if len(selected_polys) < 2:
            return {"FINISHED"}

        all_edge_keys = []
        for poly in selected_polys:
            all_edge_keys.extend(poly.edge_keys)
        shared_keys = [key for key in set(all_edge_keys) if all_edge_keys.count(key) > 1]
        if not shared_keys:
            return {"FINISHED"}

        selected_edges = get_all_selected_edges(obj)
        shared_edges = []
        for edge in selected_edges:
            if edge.key in shared_keys:
                shared_edges.append(edge)
        if not shared_edges:
            return {"FINISHED"}

        select_by_id(obj, "EDGE", [e.index for e in shared_edges], deselect=True)

        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.object.mode_set(mode="OBJECT")
        ring_edge_keys = [e.key for e in get_all_selected_edges(obj)]
        polys_to_select = []
        for poly in obj.data.polygons:
            matched_keys = [k for k in poly.edge_keys if k in ring_edge_keys]
            if len(matched_keys) == 2:
                polys_to_select.append(poly.index)

        select_by_id(obj, "FACE", polys_to_select, deselect=True)

        return {"FINISHED"}
