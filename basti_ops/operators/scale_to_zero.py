import bpy


class BastiScaleToZero(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.scale_to_zero"
    bl_label = "Scale to Zero"
    bl_options = {"REGISTER", "UNDO"}

    axis: bpy.props.EnumProperty(
        items=[
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z"),
        ],
        default="X",
    )

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
        )

    def execute(self, context):
        value = (
            0.0 if self.axis == "X" else 1.0,
            0.0 if self.axis == "Y" else 1.0,
            0.0 if self.axis == "Z" else 1.0,
        )
        bpy.ops.transform.resize(value=value)
        return {"FINISHED"}
