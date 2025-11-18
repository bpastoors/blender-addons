import bpy

from ..utils.selection import get_mesh_selection_mode


class BastiDelete(bpy.types.Operator):
    """.delete
    Execute the appropriate deletion based on the selection mode without popping up the deletion dialog.
    * Dissolve: dissolve selected elements instead"""

    bl_idname = "basti.delete"
    bl_label = "Delete"
    bl_options = {"REGISTER", "UNDO"}

    dissolve: bpy.props.BoolProperty(name="Dissolve", default=False)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
        )

    def execute(self, context):
        selection_mode = get_mesh_selection_mode(context)
        if selection_mode in ["VERT", "EDGE", "FACE"]:
            if self.dissolve:
                if selection_mode == "VERT":
                    bpy.ops.mesh.dissolve_verts()
                elif selection_mode == "EDGE":
                    bpy.ops.mesh.dissolve_edges()
                else:
                    bpy.ops.mesh.dissolve_faces()
                return {"FINISHED"}

            bpy.ops.mesh.delete(type=selection_mode)
            return {"FINISHED"}

        bpy.ops.wm.call_menu(name="VIEW3D_MT_edit_mesh_delete")
        return {"FINISHED"}
