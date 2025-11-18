import bpy


class VIEW3D_MT_BastiQuickMirror(bpy.types.Menu):
    bl_label = "Quick Mirror"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for axis in ["X", "Y", "Z"]:
            op = col.operator("basti.quick_mirror", text=axis)
            op.axis = axis
            op.pivot = "ORIGIN"
            op.scope = "ISLAND"
            op.delete_target = "ISLAND"
            op.auto_merge = True
