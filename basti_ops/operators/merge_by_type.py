import bpy

from ..utils.selection import get_mesh_selection_mode


class BastiMergeByType(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.merge_by_type"
    bl_label = "Merge at center or collapse by selection type"
    bl_options = {"REGISTER", "UNDO"}

    override_mode: bpy.props.EnumProperty(
        name="Override Mode",
        items=[
            ("NO", "No", "No"),
            ("CENTER", "Center", "Center"),
            ("CURSOR", "At Cursor", "At Cursor"),
            ("COLLAPSE", "Collapse", "Collapse"),
            ("FIRST", "To First", "To First"),
            ("LAST", "To Last", "To Last"),
        ],
        default="NO",
    )

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
        )

    def execute(self, context):
        selection_mode = get_mesh_selection_mode(context)
        mode = "COLLAPSE" if selection_mode in ["EDGE", "FACE"] else "CENTER"
        if self.override_mode != "NO":
            mode = self.override_mode
        bpy.ops.mesh.merge(type=mode)
        return {"FINISHED"}
