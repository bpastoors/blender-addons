import bmesh
import bpy
from mathutils import Vector, Euler

from ..utils.object import (
    align_euler_axis_with_direction,
    get_average_object_location,
    get_average_object_rotation_euler,
    set_object_location,
    set_object_rotation_euler,
)
from ..utils.mesh import get_average_location, get_average_normal, get_element_direction
from ..utils.selection import (
    get_mesh_selection_mode,
    get_selected,
    set_mesh_selection_mode,
)


class BastiSetPivot(bpy.types.Operator):
    """.set_pivot
    Set the pivot of selected objects.
    Origin and Cursor always work as expected, Selection and Active work with objects or elements in edit mode.
    Bounding Box and Selection in edit mode work on each object individually if multiple are selected.
    * target: what to snap the pivot to
    * orient: align object rotation to target"""

    bl_idname = "basti.set_pivot"
    bl_label = "Set pivot"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.scene is not None
            and len(context.selected_objects) > 0
            and any(o.type == "MESH" for o in context.selected_objects)
        )

    target: bpy.props.EnumProperty(
        items=[
            ("ORIGIN", "Origin", "Origin"),
            ("CURSOR", "Cursor", "Cursor"),
            ("SELECTION", "Selection", "Selection"),
            ("ACTIVE", "Active", "Active"),
            ("BB_CENTER", "Bounding Box Center", "Bounding Box Center"),
            ("BB_BOTTOM", "Bounding Box Bottom", "Bounding Box Bottom"),
            ("BB_TOP", "Bounding Box Top", "Bounding Box Top"),
            ("BB_FRONT", "Bounding Box Front", "Bounding Box Front"),
            ("BB_BACK", "Bounding Box Back", "Bounding Box Back"),
            ("BB_LEFT", "Bounding Box Left", "Bounding Box Left"),
            ("BB_RIGHT", "Bounding Box Right", "Bounding Box Right"),
        ],
        default="ACTIVE",
    )
    orient: bpy.props.BoolProperty(default=False)

    @staticmethod
    def set_location(objs: list[bpy.types.Object], location: Vector):
        for obj in objs:
            set_object_location(obj, location, True)

    @staticmethod
    def set_rotation(objs: list[bpy.types.Object], rotation: Euler):
        for obj in objs:
            set_object_rotation_euler(obj, rotation, True)

    @staticmethod
    def set_direction(obj: bpy.types.Object, direction: Vector, axis: int):
        set_mesh_selection_mode("OBJECT")
        rotation_offset = align_euler_axis_with_direction(obj, axis, direction)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        for vert in obj.data.vertices:
            vert_loc = vert.co.copy()
            vert_loc.rotate(rotation_offset.inverted())
            vert.co = vert_loc
        bm.to_mesh(obj.data)
        bm.free()

    def execute(self, context):
        selection_mode = get_mesh_selection_mode(context)
        if not selection_mode:
            return {"FINISHED"}

        objs = [o for o in context.selected_objects if o.type == "MESH"]

        target_location = None
        target_rotation = None

        if self.target == "ORIGIN":
            target_location = Vector((0.0, 0.0, 0.0))
            if self.orient:
                target_rotation = Vector((0.0, 0.0, 0.0))

        if self.target == "CURSOR":
            target_location = context.scene.cursor.location
            if self.orient:
                target_rotation = context.scene.cursor.rotation_euler

        if selection_mode == "OBJECT":
            if self.target == "ACTIVE" and context.active_object:
                target_location = context.active_object.location
                if self.orient:
                    target_rotation = context.active_object.rotation_euler
            if self.target == "SELECTION":
                target_location = get_average_object_location(objs)
                if self.orient:
                    target_rotation = get_average_object_rotation_euler(objs)

        set_mesh_selection_mode("OBJECT")

        if target_location:
            self.set_location(objs, target_location)
            if target_rotation:
                self.set_rotation(objs, target_rotation)
            return {"FINISHED"}

        target_direction_z = None
        target_direction_y = None

        for obj in objs:
            if self.target == "ACTIVE":
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                active_element = bm.select_history.active
                if not active_element:
                    continue

                target_location = get_average_location([active_element], obj)
                if self.orient:
                    target_direction_z = get_average_normal([active_element], obj)
                    target_direction_y = get_element_direction(obj, active_element)
                bm.free()

            if self.target == "SELECTION":
                if isinstance(selection_mode, tuple):
                    if selection_mode[1][0]:
                        selection_mode_temp = "VERT"
                    elif selection_mode[1][2]:
                        selection_mode_temp = "FACE"
                    elif selection_mode[1][1]:
                        selection_mode_temp = "EDGE"
                    else:
                        continue
                else:
                    selection_mode_temp = selection_mode

                selected_elements = get_selected(obj, selection_mode_temp)
                if len(selected_elements) == 0:
                    continue
                target_location = get_average_location(selected_elements, obj)
                if self.orient:
                    target_direction_z = get_average_normal(selected_elements, obj)
                    if len(selected_elements) == 1:
                        target_direction_y = get_element_direction(
                            obj, selected_elements[0]
                        )

            if self.target.startswith("BB_"):
                starting_coords = obj.matrix_world @ obj.data.vertices[0].co.copy()
                bounding_box = (
                    starting_coords,
                    starting_coords.copy(),
                )
                for vert in obj.data.vertices:
                    coords = obj.matrix_world @ vert.co.copy()
                    bounding_box[0].x = min(bounding_box[0].x, coords.x)
                    bounding_box[0].y = min(bounding_box[0].y, coords.y)
                    bounding_box[0].z = min(bounding_box[0].z, coords.z)
                    bounding_box[1].x = max(bounding_box[1].x, coords.x)
                    bounding_box[1].y = max(bounding_box[1].y, coords.y)
                    bounding_box[1].z = max(bounding_box[1].z, coords.z)

                bounding_box_center = bounding_box[0].copy()
                bounding_box_center += (bounding_box[1] - bounding_box[0]) / 2

                if self.target == "BB_CENTER":
                    target_location = bounding_box_center
                if self.target == "BB_BOTTOM":
                    target_location = bounding_box_center
                    target_location.z = bounding_box[0].z
                if self.target == "BB_TOP":
                    target_location = bounding_box_center
                    target_location.z = bounding_box[1].z
                if self.target == "BB_FRONT":
                    target_location = bounding_box_center
                    target_location.y = bounding_box[0].y
                if self.target == "BB_BACK":
                    target_location = bounding_box_center
                    target_location.y = bounding_box[1].y
                if self.target == "BB_LEFT":
                    target_location = bounding_box_center
                    target_location.x = bounding_box[0].x
                if self.target == "BB_RIGHT":
                    target_location = bounding_box_center
                    target_location.x = bounding_box[1].x

            if target_location:
                self.set_location([obj], target_location)
            if target_direction_z:
                self.set_direction(obj, target_direction_z, 2)
                if target_direction_y:
                    self.set_direction(obj, target_direction_y, 1)

        return {"FINISHED"}
