import bpy

from ..utils.object import delete_objects
from ..utils.mesh import join_meshes, copy_selected_into_new_obj


class BastiCopyToClipboard(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.copy_to_clipboard"
    bl_label = "Copy polygons to clipboard"
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
        bpy.ops.object.mode_set(mode="OBJECT")
        obj_active = context.active_object
        objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
        objs_step = []
        for obj in objs_selected:
            objs_step.append(copy_selected_into_new_obj(obj, self.cut))

        if len(objs_step) > 1:
            obj_copy = join_meshes(objs_step)
        else:
            obj_copy = objs_step[0]

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
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}
