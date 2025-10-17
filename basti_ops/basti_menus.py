import bpy


class VIEW3D_MT_BastiCreateAndCenter(bpy.types.Menu):
    bl_label = "Create and Center"

    def draw(self, context):
        object_mode = context.mode == "OBJECT"
        layout = self.layout
        pie = layout.menu_pie()

        # left
        pie.operator("mesh.primitive_plane_add", text="Draw Polygon")
        # right
        pie.operator("mesh.primitive_uv_sphere_add")
        # down
        op = pie.operator("wm.call_menu", text="Center on Axis")
        op.name = "VIEW3D_MT_BastiMoveToZero"
        # up
        pie.operator("mesh.primitive_cube_add")
        # up-left
        pie.operator("mesh.primitive_plane_add")
        # up-right
        pie.operator("mesh.primitive_cylinder_add")
        # down-left
        op = pie.operator("wm.call_menu", text="Scale to Zero")
        op.name = "VIEW3D_MT_BastiScaleToZero"
        # down-right
        op = pie.operator("wm.call_menu_pie", text="Duplicate")
        op.name = "VIEW3D_MT_BastiDuplicate"


class VIEW3D_MT_BastiDuplicate(bpy.types.Menu):
    bl_label = "Duplicate"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("basti.radial_array")
        op = pie.operator("wm.call_menu", text="Quick Mirror")
        op.name = "VIEW3D_MT_BastiQuickMirror"


class VIEW3D_MT_BastiQuickMirror(bpy.types.Menu):
    bl_label = "Quick Mirror"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        op = col.operator("basti.quick_mirror", text="X")
        op.axis = "X"
        op.delete_target = "LINKED"
        op.auto_merge = True
        op = col.operator("basti.quick_mirror", text="Y")
        op.axis = "Y"
        op.delete_target = "LINKED"
        op.auto_merge = True
        op = col.operator("basti.quick_mirror", text="Z")
        op.axis = "Z"
        op.delete_target = "LINKED"
        op.auto_merge = True


class VIEW3D_MT_BastiScaleToZero(bpy.types.Menu):
    bl_label = "Scale to Zero"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        op = col.operator("basti.scale_to_zero", text="X")
        op.axis = "X"
        op = col.operator("basti.scale_to_zero", text="Y")
        op.axis = "Y"
        op = col.operator("basti.scale_to_zero", text="Z")
        op.axis = "Z"


class VIEW3D_MT_BastiMoveToZero(bpy.types.Menu):
    bl_label = "Scale to Zero"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        op = col.operator("basti.move_to_zero", text="ALL")
        op.x, op.y, op.z = True, True, True
        op = col.operator("basti.move_to_zero", text="X")
        op.x, op.y, op.z = True, False, False
        op = col.operator("basti.move_to_zero", text="Y")
        op.x, op.y, op.z = False, True, False
        op = col.operator("basti.move_to_zero", text="Z")
        op.x, op.y, op.z = False, False, True
        op = col.operator("basti.move_to_zero", text="XY")
        op.x, op.y, op.z = True, True, False
        op = col.operator("basti.move_to_zero", text="XZ")
        op.x, op.y, op.z = True, False, True
        op = col.operator("basti.move_to_zero", text="YZ")
        op.x, op.y, op.z = False, True, True


class VIEW3D_MT_BastiModeling(bpy.types.Menu):
    bl_label = "Modeling"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("transform.shrink_fatten", text="Push")
        pie.operator("mesh.solidify", text="Thicken")


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


classes = [
    VIEW3D_MT_BastiCreateAndCenter,
    VIEW3D_MT_BastiDuplicate,
    VIEW3D_MT_BastiScaleToZero,
    VIEW3D_MT_BastiMoveToZero,
    VIEW3D_MT_BastiModeling,
    VIEW3D_MT_Basti3dView,
    VIEW3D_MT_BastiQuickMirror,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
