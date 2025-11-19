import bmesh
import bpy
from mathutils import Vector

from ..utils.object import align_euler_axis_with_direction
from ..utils.mesh import get_average_location, get_average_normal
from ..utils.selection import get_mesh_selection_mode, get_selected


class BastiSetActionCenter(bpy.types.Operator):
    """.set_cursor
    Set the location and rotation of the cursor.
    Origin and Pivot always work as expected, Selection and Pivot work with objects or elements in edit mode.
    * target: what to snap the cursor to"""

    bl_idname = "basti.set_cursor"
    bl_label = "Set cursor"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and len(context.selected_objects) > 0

    target: bpy.props.EnumProperty(
        items=[
            ("ORIGIN", "Origin", "Origin"),
            ("PIVOT", "Pivot", "Pivot"),
            ("SELECTION", "Selection", "Selection"),
            ("ACTIVE", "Active", "Active"),
        ],
        default="ORIGIN",
    )

    @staticmethod
    def align_y_axis(cursor, element, obj):
        if any(
            isinstance(element, vert_type)
            for vert_type in (bpy.types.MeshVertex, bmesh.types.BMVert)
        ):
            return
        if any(
            isinstance(element, bm_type)
            for bm_type in (bmesh.types.BMEdge, bmesh.types.BMFace)
        ):
            y_direction = (
                obj.matrix_world @ element.verts[0].co
                - obj.matrix_world @ element.verts[1].co
            )
        else:
            y_direction = (
                obj.matrix_world @ obj.data.vertices[element.vertices[0]].co
                - obj.matrix_world @ obj.data.vertices[element.vertices[1]].co
            )
        align_euler_axis_with_direction(cursor, 1, y_direction)

    def execute(self, context):
        cursor = context.scene.cursor
        selection_mode = get_mesh_selection_mode(context)
        obj_active = context.active_object or context.selected_objects[0]

        if self.target == "ORIGIN":
            cursor.location = (0.0, 0.0, 0.0)
            cursor.rotation_euler = (0.0, 0.0, 0.0)
            return {"FINISHED"}

        if self.target == "PIVOT":
            cursor.location = obj_active.location
            cursor.rotation_euler = obj_active.rotation_euler
            return {"FINISHED"}

        if not selection_mode:
            return {"FINISHED"}

        if selection_mode == "OBJECT":
            if self.target == "ACTIVE":
                cursor.location = obj_active.location
                cursor.rotation_euler = obj_active.rotation_euler
            if self.target == "SELECTION":
                objs = context.selected_objects
                average_location = Vector((0.0, 0.0, 0.0))
                average_rotation = Vector((0.0, 0.0, 0.0))
                for obj in objs:
                    average_location += obj.location
                    average_rotation += Vector([*obj.rotation_euler])
                cursor.location = average_location / len(objs)
                cursor.rotation_euler = average_rotation / len(objs)
            return {"FINISHED"}

        if self.target == "ACTIVE":
            bm = bmesh.from_edit_mesh(obj_active.data)
            active_element = bm.select_history.active
            cursor.location = get_average_location([active_element], obj_active)
            align_euler_axis_with_direction(
                cursor, 2, get_average_normal([active_element], obj_active)
            )

            self.align_y_axis(cursor, active_element, obj_active)

            bm.free()
            return {"FINISHED"}

        if self.target == "SELECTION":
            objs = context.selected_objects
            if isinstance(selection_mode, tuple):
                if selection_mode[1][0]:
                    selection_mode = "VERT"
                elif selection_mode[1][2]:
                    selection_mode = "FACE"
                elif selection_mode[1][1]:
                    selection_mode = "EDGE"
                else:
                    return {"FINISHED"}

            average_location = Vector((0.0, 0.0, 0.0))
            average_normal = Vector((0.0, 0.0, 0.0))
            used_objs = []
            for obj in objs:
                selected_elements = get_selected(obj, selection_mode)
                if len(selected_elements) == 0:
                    continue
                average_location += get_average_location(selected_elements, obj)
                average_normal += get_average_normal(selected_elements, obj)
                used_objs.append(obj)

            obj_count = len(used_objs)
            if obj_count >= 1:
                cursor.location = average_location / obj_count
                align_euler_axis_with_direction(cursor, 2, average_normal / obj_count)
            if obj_count == 1:
                selected_elements = get_selected(used_objs[0], selection_mode)
                if len(selected_elements) == 1:
                    self.align_y_axis(cursor, selected_elements[0], used_objs[0])

        return {"FINISHED"}
