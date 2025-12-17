import bpy
from pathlib import Path


class VIEW3D_PT_BastiOverview(bpy.types.Panel):
    bl_label = "Overview"
    bl_idname = "VIEW3D_PT_basti_overview"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Basti Ops"

    @staticmethod
    def get_content(target: str, pie_menu: bool = False):
        path_operators = Path(__file__).parent.parent / target
        if target == "operators":
            for file in path_operators.glob("*.py"):
                yield file.stem
        for file in path_operators.glob("*.py"):
            file_text = file.read_text()
            label = file_text.split('bl_label = "', 1)[1].split('"', 1)[0]
            if target == "menus":
                pie_in_text = "pie = layout.menu_pie()" in file_text
                if pie_menu != pie_in_text:
                    continue
                class_name = file_text.split("class ", 1)[1].split("(bpy.", 1)[0]
                yield class_name, label
            if target == "panels":
                if label == "Overview":
                    continue
                id_name = file_text.split('bl_idname = "', 1)[1].split('"', 1)[0]
                yield id_name, label

    def draw(self, context):
        layout = self.layout

        layout.separator(type="LINE")
        layout.label(text="Menus")
        for menu in self.get_content("menus", False):
            op = layout.operator("wm.call_menu", text=menu[1])
            op.name = menu[0]

        layout.separator(type="LINE")
        layout.label(text="Pie-Menus")
        for menu in self.get_content("menus", True):
            op = layout.operator("wm.call_menu", text=menu[1])
            op.name = menu[0]

        layout.separator(type="LINE")
        layout.label(text="Panels")
        for panel in self.get_content("panels"):
            op = layout.operator("wm.call_panel", text=panel[1])
            op.name = panel[0]

        layout.separator(type="LINE")
        layout.label(text="Operators")
        for op in self.get_content("operators"):
            layout.operator(f"basti.{op}")
