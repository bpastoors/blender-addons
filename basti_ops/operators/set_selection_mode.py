import bpy

from ..utils.selection import set_mesh_selection_mode


class BastiSetSelectionMode(bpy.types.Operator):
    bl_idname = "basti.set_selection_mode"
    bl_label = "Set Mesh Selection Mode"
    bl_options = {"REGISTER", "UNDO"}

    selection_mode: bpy.props.EnumProperty(
        items=[
            ("VERT", "VERT", "Vertex"),
            ("EDGE", "EDGE", "Edge"),
            ("FACE", "FACE", "Face"),
            ("OBJECT", "OBJECT", "Object"),
            ("SCULPT", "SCULPT", "Sculpt"),
        ],
        default="OBJECT")

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        return context.active_object.type == 'CURVE' or context.active_object.type == 'MESH'

    def execute(self, context):
        set_mesh_selection_mode(self.selection_mode, curve=context.active_object.type == 'CURVE')
        return {"FINISHED"}
