import bpy

from ..utils.selection import get_selected_vertices
from ..utils.mesh import get_average_location


class BastiMoveToZero(bpy.types.Operator):
    """.move_to_zero
    Move the selection to zero on the selected axis in world-space.
    * X: move to zero on X axis
    * Y: move to zero on Y axis
    * Z: move to zero on Z axis"""

    bl_idname = "basti.move_to_zero"
    bl_label = "Move to Zero"
    bl_options = {"REGISTER", "UNDO"}

    x: bpy.props.BoolProperty(name="X", default=True)
    y: bpy.props.BoolProperty(name="Y", default=True)
    z: bpy.props.BoolProperty(name="Z", default=True)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        if (
            context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
        ):
            verts_selected = get_selected_vertices(obj)
            center = get_average_location(verts_selected, obj)
            value = (
                center[0] * -1.0 if self.x else 0.0,
                center[1] * -1.0 if self.y else 0.0,
                center[2] * -1.0 if self.z else 0.0,
            )
            bpy.ops.transform.translate(value=value, orient_type="GLOBAL")
        else:
            obj.location = (
                0.0 if self.x else obj.location[0],
                0.0 if self.y else obj.location[1],
                0.0 if self.z else obj.location[2],
            )
        return {"FINISHED"}
