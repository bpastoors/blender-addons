import bpy

from ..utils.raycast import raycast
from ..utils.material import (
    create_new_material,
    get_material_of_polygon,
    apply_material_on_selected_faces,
)


class BastiApplyMaterial(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "basti.apply_material"
    bl_label = "apply material under cursor to selected polygons"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        raycast_result, _, _, polygon_index, obj_target = raycast(context, self.coords)

        if not raycast_result:
            new_mat = create_new_material()
        else:
            new_mat = get_material_of_polygon(obj_target, polygon_index)

        apply_material_on_selected_faces(context, new_mat)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)
