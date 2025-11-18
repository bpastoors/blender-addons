import bpy


class VIEW3D_PT_BastiOverview(bpy.types.Panel):
    bl_label = "Cursor Properties"
    bl_idname = "VIEW3D_PT_basti_overview"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Basti Ops"

    def draw(self, context):
        layout = self.layout

        layout.separator(type="LINE")
        layout.label(text="Menus")
        for menu in [
            ("VIEW3D_MT_BastiQuickMirror", "Quick Mirror"),
            ("VIEW3D_MT_BastiScaleToZero", "Scale to Zero"),
            ("VIEW3D_MT_BastiMoveToZero", "Move to Zero"),
        ]:
            op = layout.operator("wm.call_menu", text=menu[1])
            op.name = menu[0]

        layout.separator(type="LINE")
        layout.label(text="Pie-Menus")
        for menu in [
            ("VIEW3D_MT_Basti3dSettings", "3d Settings"),
            ("VIEW3D_MT_Basti3dView", "3d View"),
            ("VIEW3D_MT_BastiModeling", "Modeling"),
            ("VIEW3D_MT_BastiCreateAndCenter", "Create and Center"),
            ("VIEW3D_MT_BastiDuplicate", "Duplicate"),
        ]:
            op = layout.operator("wm.call_menu_pie", text=menu[1])
            op.name = menu[0]

        layout.separator(type="LINE")
        layout.label(text="Panels")
        for panel in [
            ("VIEW3D_PT_basti_action_center", "Action Center"),
            ("VIEW3D_PT_basti_cursor", "Cursor"),
        ]:
            op = layout.operator("wm.call_panel", text=panel[1])
            op.name = panel[0]

        layout.separator(type="LINE")
        layout.label(text="Operators")
        for op in [
            "bevel",
            "connect_or_knife",
            "copy_to_clipboard",
            "delete",
            "linear_array",
            "loop_slice",
            "make_face",
            "merge_by_type",
            "move_to_zero",
            "paste_from_clipboard",
            "quick_mirror",
            "radial_array",
            "rotate_to_zero",
            "scale_to_zero",
            "scatter_duplicate",
            "select_edge_or_island",
            "select_loop",
            "set_action_center",
            "set_cursor",
            "set_selection_mode",
            "set_viewpoint",
            "toggle_sculpt_automasking",
        ]:
            layout.operator(f"basti.{op}")

        layout.separator(type="LINE")
        layout.label(text="Operators with Mouse-Target")
        for op in [
            "apply_material",
            "copy_to_mesh",
            "move_to_face",
        ]:
            layout.operator(f"basti.{op}")
