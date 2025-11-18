import bpy


class VIEW3D_PT_BastiActionCenter(bpy.types.Panel):
    bl_label = "Action Center"
    bl_idname = "VIEW3D_PT_basti_action_center"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    def draw(self, context):
        layout = self.layout

        layout.operator_enum("basti.set_action_center", "action_center")

        layout.separator(type="LINE")
        layout.label(text="Orientation")
        layout.props_enum(context.scene.transform_orientation_slots[0], "type")
        layout.separator(type="SPACE")
        layout.label(text="Pivot")
        layout.props_enum(context.scene.tool_settings, "transform_pivot_point")
