import bpy

from ..utils.selection import mesh_selection_mode


class BastiBevel(bpy.types.Operator):
    """execute right bevel tool based on selection"""

    bl_idname = "basti.bevel"
    bl_label = "Bevel"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
        )

    def execute(self, context):
        submesh_mode = mesh_selection_mode(context)
        if submesh_mode == "VERT":
            bpy.ops.mesh.bevel("INVOKE_DEFAULT", affect="VERTICES")
        elif submesh_mode == "EDGE":
            bpy.ops.mesh.bevel("INVOKE_DEFAULT", affect="EDGES")
        elif submesh_mode == "FACE":
            bpy.ops.view3d.edit_mesh_extrude_move_normal()
        return {"FINISHED"}
