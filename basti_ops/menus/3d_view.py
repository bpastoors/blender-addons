import bpy


class VIEW3D_MT_Basti3dView(bpy.types.Menu):
    bl_label = "3d Viewpoint"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # left
        op = pie.operator("basti.set_viewpoint", text="Left")
        op.viewpoint = "LEFT"
        # right
        op = pie.operator("basti.set_viewpoint", text="Right")
        op.viewpoint = "RIGHT"
        # down
        op = pie.operator("basti.set_viewpoint", text="Bottom")
        op.viewpoint = "BOTTOM"
        # up
        op = pie.operator("basti.set_viewpoint", text="Top")
        op.viewpoint = "TOP"
        # up-left
        pie.operator("view3d.view_camera", text="Camera")
        # up-right
        op = pie.operator("basti.set_viewpoint", text="Perspective")
        op.viewpoint = "PERSPECTIVE"
        # down-left
        op = pie.operator("basti.set_viewpoint", text="Back")
        op.viewpoint = "BACK"
        # down-right
        op = pie.operator("basti.set_viewpoint", text="Front")
        op.viewpoint = "FRONT"
