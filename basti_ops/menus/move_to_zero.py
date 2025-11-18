import bpy


class VIEW3D_MT_BastiMoveToZero(bpy.types.Menu):
    bl_label = "Move to Zero"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for key, settings in {
            "ALL": (True, True, True),
            "X": (True, False, False),
            "Y": (False, True, False),
            "Z": (False, False, True),
            "XY": (True, True, False),
            "XZ": (True, False, True),
            "YZ": (False, True, True),
        }.items():
            op = col.operator("basti.move_to_zero", text=key)
            op.x, op.y, op.z = settings
