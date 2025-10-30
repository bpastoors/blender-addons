import bpy


class VIEW3D_MT_Basti3dSettings(bpy.types.Menu):
    bl_label = "3d Settings"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("view3d.localview", text="Toggle Isolate")
        pie.operator("view3d.toggle_xray", text="Toggle X-Ray")
