import bpy


class VIEW3D_MT_BastiModeling(bpy.types.Menu):
    bl_label = "Modeling"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("transform.shrink_fatten", text="Push")
        pie.operator("mesh.solidify", text="Thicken")
        op = pie.operator("wm.call_menu", text="Scale to Zero")
        op.name = "VIEW3D_MT_BastiScaleToZero"
