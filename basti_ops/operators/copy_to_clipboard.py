import bpy

from ..utils.selection import get_mesh_selection_mode, set_mesh_selection_mode
from ..utils.object import delete_objects
from ..utils.mesh import join_meshes, copy_selected_into_new_obj


class BastiCopyToClipboard(bpy.types.Operator):
    """.copy_to_clipboard
    Copy the selected mesh elements to the clipboard.
    * cut: delete selected elements - cutting instead of copying"""

    bl_idname = "basti.copy_to_clipboard"
    bl_label = "Copy to clipboard"
    bl_options = {"REGISTER", "UNDO"}

    cut: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
        )

    def execute(self, context):
        selection_mode = get_mesh_selection_mode(bpy.context)
        set_mesh_selection_mode("OBJECT")
        obj_active = context.active_object
        objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
        objs_step = [copy_selected_into_new_obj(o, self.cut) for o in objs_selected]

        obj_copy = join_meshes(objs_step)
        obj_copy["basti_material_backup"] = [m.name for m in obj_copy.material_slots]

        context = {
            "object": obj_copy,
            "active_object": obj_copy,
            "selected_objects": [obj_copy],
            "selected_editable_objects": [obj_copy],
        }

        with bpy.context.temp_override(**context):
            bpy.ops.view3d.copybuffer()

        delete_objects([obj_copy])

        for obj in objs_selected:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = obj_active
        set_mesh_selection_mode(selection_mode)
        return {"FINISHED"}
