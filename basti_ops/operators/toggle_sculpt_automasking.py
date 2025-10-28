import bpy

from ..utils.selection import mesh_selection_mode


class BastiToggleSculptAutomasking(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.toggle_sculpt_automasking"
    bl_label = "Toggle Sculpt Automasking"
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("BOUNDARY_EDGES", "Boundary Edges", "Boundary Edges"),
            ("BOUNDARY_FACE_SETS", "Boundary Face Sets", "Boundary Face Sets"),
            ("CAVITY", "Cavity", "Cavity"),
            ("CAVITY_INVERTED", "Cavity Inverted", "Cavity Inverted"),
            ("CAVITY_CURVE", "Custom Cavity Curve", "Custom Cavity Curve"),
            ("FACE_SETS", "Face Sets", "Face Sets"),
            ("START_NORMAL", "Start Normal", "Start Normal"),
            ("TOPOLOGY", "Topology", "Topology"),
            ("VIEW_NORMAL", "View Normal", "View Normal"),
            ("VIEW_OCCLUSION", "View Occlusion", "View Occlusion"),
        ],
        default="TOPOLOGY",
    )

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "SCULPT"
        )

    def execute(self, context):
        try:
            if self.mode == "BOUNDARY_EDGES":
                bpy.context.tool_settings.sculpt.use_automasking_boundary_edges = (
                    not context.tool_settings.sculpt.use_automasking_boundary_edges
                )
            elif self.mode == "BOUNDARY_FACE_SETS":
                bpy.context.tool_settings.sculpt.use_automasking_boundary_face_sets = (
                    not context.tool_settings.sculpt.use_automasking_boundary_face_sets
                )
            elif self.mode == "CAVITY":
                bpy.context.tool_settings.sculpt.use_automasking_cavity = (
                    not context.tool_settings.sculpt.use_automasking_cavity
                )
            elif self.mode == "CAVITY_INVERTED":
                bpy.context.tool_settings.sculpt.use_automasking_cavity_inverted = (
                    not context.tool_settings.sculpt.use_automasking_cavity_inverted
                )
            elif self.mode == "CAVITY_CURVE":
                bpy.context.tool_settings.sculpt.use_automasking_custom_cavity_curve = (
                    not context.tool_settings.sculpt.use_automasking_custom_cavity_curve
                )
            elif self.mode == "FACE_SETS":
                bpy.context.tool_settings.sculpt.use_automasking_face_sets = (
                    not context.tool_settings.sculpt.use_automasking_face_sets
                )
            elif self.mode == "START_NORMAL":
                bpy.context.tool_settings.sculpt.use_automasking_start_normal = (
                    not context.tool_settings.sculpt.use_automasking_start_normal
                )
            elif self.mode == "TOPOLOGY":
                bpy.context.tool_settings.sculpt.use_automasking_topology = (
                    not context.tool_settings.sculpt.use_automasking_topology
                )
            elif self.mode == "VIEW_NORMAL":
                bpy.context.tool_settings.sculpt.use_automasking_view_normal = (
                    not context.tool_settings.sculpt.use_automasking_view_normal
                )
            elif self.mode == "VIEW_OCCLUSION":
                bpy.context.tool_settings.sculpt.use_automasking_view_occlusion = (
                    not context.tool_settings.sculpt.use_automasking_view_occlusion
                )
        except:
            return {"CANCELLED"}
        # print(mode_mapping[self.mode])
        return {"FINISHED"}
