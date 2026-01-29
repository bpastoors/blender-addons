import bpy


class VIEW3D_MT_BastiSetPivot(bpy.types.Menu):
    bl_label = "Set Pivot"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for target in [
            "ORIGIN",
            "CURSOR",
            "SELECTION",
            "ACTIVE",
            "BB_CENTER",
            "BB_BOTTOM",
            "BB_TOP",
            "BB_FRONT",
            "BB_BACK",
            "BB_LEFT",
            "BB_RIGHT",
        ]:
            op = col.operator("basti.set_pivot", text=target)
            op.target = target
