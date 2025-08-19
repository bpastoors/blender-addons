import bpy

from .util_selection import set_mesh_selection_mode


class BastiSetSelectionMode(bpy.types.Operator):
    bl_idname = "basti.set_selection_mode"
    bl_label = "Set Mesh Selection Mode"
    bl_options = {"REGISTER", "UNDO"}

    selection_mode: bpy.props.EnumProperty(
        items=[
            ("VERT", "VERT", "Vertex"),
            ("EDGE", "EDGE", "Edge"),
            ("FACE", "FACE", "Face"),
            ("OBJECT", "OBJECT", "Object")
        ],
        default="OBJECT")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        set_mesh_selection_mode(self.selection_mode)
        return {"FINISHED"}
