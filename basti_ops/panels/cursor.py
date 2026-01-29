import bpy


class VIEW3D_PT_BastiCursor(bpy.types.Panel):
    bl_label = "Cursor Properties"
    bl_idname = "VIEW3D_PT_basti_cursor"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    def draw(self, context):
        layout = self.layout
        layout.operator_enum("basti.set_cursor", "target")
        layout.separator(type="LINE")

        layout.prop(context.scene.cursor, "location")
        layout.prop(context.scene.cursor, "rotation_euler")
