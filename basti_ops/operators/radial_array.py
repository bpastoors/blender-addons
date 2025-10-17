import math

import bpy

from ..utils.selection import mesh_selection_mode
from ..utils.mesh import join_meshes, copy_selected_into_new_obj


class BastiRadialArray(bpy.types.Operator):
    """Duplicate selected faces around the cursor"""

    bl_idname = "basti.radial_array"
    bl_label = "Radial Array"
    bl_options = {"REGISTER", "UNDO"}

    pivot: bpy.props.EnumProperty(
        items=[
            ("ORIGIN", "Origin", "World Origin"),
            ("PIVOT", "Pivot", "Object Pivot"),
            ("CURSOR", "Cursor", "3d Cursor"),
        ],
        default="ORIGIN",
    )
    axis: bpy.props.EnumProperty(
        items=[
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z"),
        ],
        default="Z",
    )
    count: bpy.props.IntProperty(default=4)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
            and mesh_selection_mode(context) == "FACE"
        )

    def execute(self, context):
        from mathutils import Matrix, Vector

        active_object = context.active_object
        rotation_pivot = Vector()
        if self.pivot == "PIVOT":
            rotation_pivot = active_object.location
        elif self.pivot == "CURSOR":
            rotation_pivot = context.scene.cursor.location
        rotation_rad = 2 * math.pi / self.count
        step_objects = []
        bpy.ops.object.mode_set(mode="OBJECT")
        for i in range(1, self.count):
            new_obj = copy_selected_into_new_obj(active_object, False)
            for vert in new_obj.data.vertices:
                coords = bpy.context.object.matrix_world @ Vector(vert.co.copy())
                coords -= rotation_pivot
                coords = coords @ Matrix.Rotation(rotation_rad * i, 4, self.axis)
                coords += rotation_pivot
                vert.co = bpy.context.object.matrix_world.inverted() @ coords
            step_objects.append(new_obj)
        join_meshes([active_object, *step_objects])

        active_object.select_set(True)
        bpy.context.view_layer.objects.active = active_object
        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}
