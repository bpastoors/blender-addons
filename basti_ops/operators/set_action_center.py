import bpy


class BastiSetActionCenter(bpy.types.Operator):
    """.set_action_center
    Set the transform pivot and orientation based on action center presets.
    * action_center: the preset to set"""

    bl_idname = "basti.set_action_center"
    bl_label = "Set Tool Center and Orientation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    action_center: bpy.props.EnumProperty(
        items=[
            ("GLOBAL", "Global", "Global"),
            ("OBJECT", "Object", "Object"),
            ("SCREEN", "Screen", "Screen"),
            ("ACTIVE_CENTER", "Active Center", "Active Center"),
            ("NORMAL_SELECTION", "Normal Selection", "Normal Selection"),
            ("NORMAL_ACTIVE", "Normal Active", "Normal Active"),
            ("NORMAL_INDIVIDUAL", "Normal Individual", "Normal Individual"),
            ("CURSOR", "Cursor", "Cursor"),
        ],
        default="GLOBAL",
    )

    mapping = {
        "GLOBAL": ("BOUNDING_BOX_CENTER", "GLOBAL", "CENTER"),
        "OBJECT": ("BOUNDING_BOX_CENTER", "LOCAL", "CENTER"),
        "SCREEN": ("BOUNDING_BOX_CENTER", "VIEW", "CENTER"),
        "ACTIVE_CENTER": ("ACTIVE_ELEMENT", "GLOBAL", "ACTIVE"),
        "NORMAL_SELECTION": ("BOUNDING_BOX_CENTER", "NORMAL", "CENTER"),
        "NORMAL_ACTIVE": ("ACTIVE_ELEMENT", "NORMAL", "ACTIVE"),
        "NORMAL_INDIVIDUAL": ("INDIVIDUAL_ORIGINS", "NORMAL", "CENTER"),
        "CURSOR": ("CURSOR", "CURSOR", "CENTER"),
    }

    def execute(self, context):
        mapping = self.mapping[self.action_center]
        context.scene.tool_settings.transform_pivot_point = mapping[0]
        context.scene.transform_orientation_slots[0].type = mapping[1]
        context.scene.tool_settings.snap_target = mapping[2]
        return {"FINISHED"}
