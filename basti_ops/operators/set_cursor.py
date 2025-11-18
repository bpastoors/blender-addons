import bmesh
import bpy
from mathutils import Vector

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
            elements = [bm.select_history[-1]]
            cursor.location = get_average_location(elements, obj_active)
            cursor.rotation_euler = get_average_normal(elements, obj_active)
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
            obj_count = len(objs)
            for obj in objs:
                selected_elements = get_selected(obj, selection_mode)
                if len(selected_elements) == 0:
                    obj_count -= 1
                    continue
                average_location += get_average_location(selected_elements, obj)
                average_normal += get_average_normal(selected_elements, obj)
            if obj_count < 1:
                obj_count = 1
            cursor.location = average_location / obj_count
            cursor.rotation_euler = (
                Vector((0.0, 0.0, 1.0))
                .rotation_difference(average_normal / obj_count)
                .to_euler()
            )

        return {"FINISHED"}
