import bpy

from ..utils.mesh import join_meshes, copy_selected_into_new_obj
from ..utils.raycast import raycast

class BastiCopyToMesh(bpy.types.Operator):
    bl_idname = "basti.copy_to_mesh"
    bl_label = "Copy/Paste polygons into mesh under Cursor"
    bl_options = {"REGISTER", "UNDO"}

    cut: bpy.props.BoolProperty(default=False)

    def copy_cut_to_mesh(self, context, coords, cut=False):
        raycast_result, _, _, _, obj_target = raycast(context, coords)

        bpy.ops.object.mode_set(mode="OBJECT")
        objs_selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
        objs_to_join = []
        for obj in objs_selected:
            objs_to_join.append(copy_selected_into_new_obj(obj, cut))

        if raycast_result and obj_target.type == "MESH":
            bpy.ops.mesh.select_all(action="DESELECT")
            objs_to_join.insert(0, obj_target)

        obj_target = join_meshes(objs_to_join)

        obj_target.select_set(True)
        bpy.context.view_layer.objects.active = obj_target
        bpy.ops.object.mode_set(mode="EDIT")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT'

    def execute(self, context):
        self.copy_cut_to_mesh(context, self.coords, self.cut)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.coords = event.mouse_region_x, event.mouse_region_y
        return self.execute(context)
