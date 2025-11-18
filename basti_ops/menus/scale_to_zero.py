import bpy


class VIEW3D_MT_BastiScaleToZero(bpy.types.Menu):
    bl_label = "Scale to Zero"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for axis in ["X", "Y", "Z"]:
            op = col.operator("basti.scale_to_zero", text=axis)
            op.axis = axis
