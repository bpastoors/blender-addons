import bpy


class BastiCopyModifiers(bpy.types.Operator):
    """.copy_modifiers
    Copy all modifiers and the properties of the active object to all selected objects.
    * append: keep existing modifiers on the target object
    * move: remove modifiers from the active object"""

    bl_idname = "basti.copy_modifiers"
    bl_label = "Copy Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    append: bpy.props.BoolProperty(default=False)
    move: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj_active = context.active_object
        objs_selected = [
            o for o in context.selected_objects if o.type == "MESH" and o != obj_active
        ]

        for obj in objs_selected:
            if len(obj.modifiers) > 0 and not self.append:
                obj.modifiers.clear()
            for mod in obj_active.modifiers:
                mod_new = obj.modifiers.new(mod.name, mod.type)
                for prop in mod.rna_type.properties:
                    if not prop.is_readonly:
                        prop_id = prop.identifier
                        attr_value = getattr(mod, prop_id)

                        try:
                            setattr(mod_new, prop_id, attr_value)
                        except AttributeError:
                            # Some properties are not writable even if not marked read-only
                            pass

        if self.move:
            obj_active.modifiers.clear()

        return {"FINISHED"}
