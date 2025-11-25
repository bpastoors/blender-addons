import bmesh
import bpy
from bpy_extras import view3d_utils

from ..utils.selection import (
    get_mesh_selection_mode,
    set_mesh_selection_mode,
    force_deselect_all,
    get_selected,
    select_objects,
    select_by_id,
)
from ..utils.object import add_new_mesh_object
from ..utils.ui import set_status_text, clear_status_text


class BastiMakePolygon(bpy.types.Operator):
    """.make_polygon"""

    bl_idname = "basti.make_polygon"
    bl_label = "Make Polygon"
    bl_options = {"REGISTER", "UNDO"}

    obj = None
    bm = None
    initial_active_object = []
    initial_selection_mode = None
    initial_selection = {}
    vertices = []
    edges = []
    current_vert = None
    current_vert_initial_location = None

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

    def invoke(self, context, event):
        self.initial_active_object = context.active_object
        self.initial_selection_mode = get_mesh_selection_mode(context)

        selection_mode = (
            self.initial_selection_mode
            if isinstance(self.initial_selection_mode, str)
            and self.initial_selection_mode != "OBJECT"
            else "VERT"
        )

        for obj in context.selected_objects:
            self.initial_selection[obj.name] = get_selected(
                obj, selection_mode, get_index=True
            )
            force_deselect_all(obj)

        if self.initial_selection_mode == "OBJECT":
            self.obj = add_new_mesh_object(
                "make_polygon", set_active=True, next_to_obj=self.initial_active_object
            )
        else:
            self.obj = self.initial_active_object

        set_mesh_selection_mode("VERT")
        self.bm = bmesh.from_edit_mesh(self.obj.data)
        self.bm.verts.ensure_lookup_table()
        bmesh.update_edit_mesh(self.obj.data)

        context.window_manager.modal_handler_add(self)

        set_status_text(
            [
                ("MOUSE_LMB", "Add Point"),
                ("MOUSE_RMB", "Remove Last"),
                ("KEY_SHIFT", ""),
                ("MOUSE_LMB", "Start New"),
                ("KEY_RETURN", "Finish"),
                ("EVENT_SPACEKEY", "    Finish"),
                ("EVENT_ESC", " Cancel"),
            ]
        )
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "ESC" and event.value == "PRESS":
            self.handle_cancel()
            return {"CANCELLED"}

        if event.type == "RET" and event.value == "PRESS":
            self.handle_finish()
            return {"FINISHED"}

        if event.type == "SPACE" and event.value == "PRESS":
            self.handle_finish()
            return {"FINISHED"}

        if event.shift and event.type == "LEFTMOUSE" and event.value == "PRESS":
            self.handle_restart(self.get_location(context, event))
            return {"RUNNING_MODAL"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            self.handle_start_vertex(self.get_location(context, event))
            return {"RUNNING_MODAL"}

        if event.type == "LEFTMOUSE" and event.value == "RELEASE" and self.current_vert:
            self.handle_finish_vertex()
            return {"RUNNING_MODAL"}

        if event.type == "MOUSEMOVE" and self.current_vert:
            self.handle_update_vertex(self.get_location(context, event))
            return {"RUNNING_MODAL"}

        if event.type == "RIGHTMOUSE" and event.value == "PRESS":
            self.handle_remove_last_vertex()
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def handle_cancel(self):
        if self.vertices:
            for vert in self.vertices:
                self.bm.verts.remove(vert)
        select_objects(
            [self.initial_active_object]
            + [
                bpy.data.objects[name]
                for name in self.initial_selection.keys()
                if name != self.initial_active_object.name
            ],
            clear_selection=False,
            set_active=True,
        )
        selection_mode = (
            self.initial_selection_mode
            if isinstance(self.initial_selection_mode, str)
            and self.initial_selection_mode != "OBJECT"
            else "VERT"
        )
        for obj_name, ids in self.initial_selection.items():
            select_by_id(bpy.data.objects[obj_name], selection_mode, ids)

        if self.initial_selection_mode == "OBJECT":
            self.bm.free()
            self.bm = None
            bpy.data.objects.remove(self.obj)

        self.wrap_up(self.initial_selection_mode)

    def handle_finish(self):
        selection_mode = "FACE"
        if len(self.vertices) > 2:
            new_face = self.bm.faces.new(self.vertices)
            set_mesh_selection_mode(selection_mode)
            new_face.select_set(True)
        else:
            selection_mode = "VERT"
            set_mesh_selection_mode(selection_mode)
            for vert in self.vertices:
                vert.select_set(True)
        self.wrap_up(selection_mode)

    def handle_restart(self, location):
        self.handle_finish()
        set_mesh_selection_mode("VERT")
        self.bm = bmesh.from_edit_mesh(self.obj.data)
        self.handle_start_vertex(location)

    def handle_remove_last_vertex(self):
        if not self.vertices:
            return
        if len(self.vertices) > 2:
            self.bm.edges.remove(self.edges.pop(0))
        self.bm.verts.remove(self.vertices.pop())

        self.vertices[-1].select_set(True)
        self.bm.select_history.add(self.vertices[-1])
        if len(self.vertices) > 2:
            closing_edge = self.bm.edges.new([self.vertices[-1], self.vertices[0]])
            self.edges.insert(0, closing_edge)
        bmesh.update_edit_mesh(self.obj.data)

    def handle_start_vertex(self, location):
        if not location:
            return

        if len(self.vertices) > 0:
            self.vertices[-1].select_set(False)
            self.bm.select_history.discard(self.vertices[-1])
        vert = self.bm.verts.new(self.obj.matrix_world.inverted() @ location)
        self.vertices.append(vert)
        self.current_vert = vert
        self.current_vert_initial_location = location

        vert.select_set(True)
        self.bm.select_history.add(vert)
        bmesh.update_edit_mesh(self.obj.data)
        self.bm.verts.ensure_lookup_table()

        if len(self.vertices) > 1:
            prev_vert = self.vertices[-2]
            new_edge = self.bm.edges.new([prev_vert, vert])
            self.edges.append(new_edge)

            if len(self.vertices) > 2:
                if len(self.vertices) > 3:
                    pop_edge = self.edges.pop(0)
                    self.bm.edges.remove(pop_edge)
                closing_edge = self.bm.edges.new([vert, self.vertices[0]])
                self.edges.insert(0, closing_edge)

        bmesh.update_edit_mesh(self.obj.data)

    def handle_finish_vertex(self):
        self.current_vert = None
        self.current_vert_initial_location = None

    def handle_update_vertex(self, location):
        if not location:
            return
        self.current_vert.co = self.obj.matrix_world.inverted() @ location

        bmesh.update_edit_mesh(self.obj.data)

    def handle_cancel_vertex(self):
        if self.current_vert:
            self.handle_update_vertex(self.current_vert_initial_location)
        self.current_vert = None
        self.current_vert_initial_location = None

    def wrap_up(self, selection_mode: str):
        if self.bm:
            bmesh.update_edit_mesh(self.obj.data)
            self.bm.free()
        self.vertices.clear()
        self.edges.clear()
        self.current_vert = None

        set_mesh_selection_mode("OBJECT")
        set_mesh_selection_mode(selection_mode)
        clear_status_text()

    @staticmethod
    def get_location(context, event):
        region = context.region
        rv3d = context.region_data

        coord = (event.mouse_region_x, event.mouse_region_y)

        # Cast ray into the scene
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        # Get the camera view direction (normalized)
        view_direction = view_vector.normalized()

        # Determine which axis is most aligned with the view direction
        abs_x = abs(view_direction.x)
        abs_y = abs(view_direction.y)
        abs_z = abs(view_direction.z)

        # Choose the plane based on which axis has the largest component
        if abs_z >= abs_x and abs_z >= abs_y:
            # Project onto XY plane (Z = 0)
            if view_vector.z != 0:
                factor = -ray_origin.z / view_vector.z
                return ray_origin + factor * view_vector
        if abs_y >= abs_x and abs_y >= abs_z:
            # Project onto XZ plane (Y = 0)
            if view_vector.y != 0:
                factor = -ray_origin.y / view_vector.y
                return ray_origin + factor * view_vector
        # Project onto YZ plane (X = 0)
        if view_vector.x != 0:
            factor = -ray_origin.x / view_vector.x
            return ray_origin + factor * view_vector

        return None
