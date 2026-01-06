import bpy


class BastiSetViewpoint(bpy.types.Operator):
    """.set_viewpoint
    Set the view axis and toggle between orthographic and perspective view. All directions are orthographic
    * viewpoint: the viewpoint to switch to"""

    bl_idname = "basti.set_viewpoint"
    bl_label = "Set 3d View Viewpoint"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    viewpoint: bpy.props.EnumProperty(
        items=[
            ("TOP", "Top", "Top"),
            ("BOTTOM", "Bottom", "Bottom"),
            ("LEFT", "Left", "Left"),
            ("RIGHT", "Right", "Right"),
            ("FRONT", "Front", "Front"),
            ("BACK", "Back", "Back"),
            ("PERSPECTIVE", "Perspective", "Perspective"),
        ],
        default="PERSPECTIVE",
    )

    def execute(self, context):
        is_perspective = False
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                is_perspective = area.spaces.active.region_3d.is_perspective
        if self.viewpoint == "PERSPECTIVE":
            if not is_perspective:
                new_location = context.scene.pop("basti_camera_location_backup", None)
                new_rotation = context.scene.pop("basti_camera_rotation_backup", None)

                bpy.ops.view3d.view_persportho()

                if new_location is not None:
                    context.region_data.view_location = new_location
                if new_rotation is not None:
                    context.region_data.view_rotation = new_rotation

            return {"FINISHED"}

        if is_perspective:
            context.scene["basti_camera_location_backup"] = (
                context.region_data.view_location
            )
            context.scene["basti_camera_rotation_backup"] = (
                context.region_data.view_rotation
            )
            bpy.ops.view3d.view_persportho()
        bpy.ops.view3d.view_axis(type=self.viewpoint)
        return {"FINISHED"}
