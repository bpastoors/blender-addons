import bpy

from ..utils.object import delete_objects
from ..utils.mesh import join_meshes
from ..utils.selection import (
    get_mesh_selection_mode,
    set_mesh_selection_mode,
    force_deselect_all,
)


class BastiPasteFromClipboard(bpy.types.Operator):
    """.paste_from_clipboard
    Paste elements copied with **.copy_to_clipboard** into the currently selected mesh
    """

    bl_idname = "basti.paste_from_clipboard"
    bl_label = "Paste from Clipboard"
    bl_options = {"REGISTER", "UNDO"}

    cleanup_materials: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj_target = context.active_object
        selection_mode = get_mesh_selection_mode(context)
        force_deselect_all(obj_target)
        set_mesh_selection_mode("OBJECT")

        objs_before = set(bpy.data.objects)
        bpy.ops.view3d.pastebuffer(autoselect=True)
        obj_pasted = list(set(bpy.data.objects) - objs_before)[0]

        if not obj_pasted.type == "MESH":
            delete_objects([obj_pasted])
        else:
            if self.cleanup_materials:
                self.reuse_existing_materials(obj_pasted)
            join_meshes([obj_target, obj_pasted])

        set_mesh_selection_mode(selection_mode)
        return {"FINISHED"}

    @staticmethod
    def reuse_existing_materials(obj: bpy.types.Object):
        material_backups = obj.get("basti_material_backup")
        material_copies = {m.name for m in obj.material_slots}
        if material_backups and len(material_backups) == len(obj.material_slots):
            for i in range(len(material_backups)):
                if material_backups[i] in bpy.data.materials:
                    obj.material_slots[i].material = bpy.data.materials[
                        material_backups[i]
                    ]
            for material_name in material_copies:
                if material_name not in obj.material_slots:
                    bpy.data.materials.remove(bpy.data.materials[material_name])
