import bpy


class VIEW3D_MT_BastiDuplicate(bpy.types.Menu):
    bl_label = "Duplicate"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("basti.radial_array")
        op = pie.operator("wm.call_menu", text="Quick Mirror")
        op.name = "VIEW3D_MT_BastiQuickMirror"
        pie.operator("basti.linear_array")
        pie.operator("basti.scatter_duplicate")
