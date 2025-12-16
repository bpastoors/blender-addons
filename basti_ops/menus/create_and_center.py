import bpy


class VIEW3D_MT_BastiCreateAndCenter(bpy.types.Menu):
    bl_label = "Create and Center"

    def draw(self, context):
        object_mode = context.mode == "OBJECT"
        layout = self.layout
        pie = layout.menu_pie()

        # left
        pie.operator("basti.make_polygon", text="Draw Polygon")
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
