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


class VIEW3D_MT_BastiDuplicate(bpy.types.Menu):
    bl_label = "Duplicate"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("basti.radial_array")
        op = pie.operator("wm.call_menu", text="Quick Mirror")
        op.name = "VIEW3D_MT_BastiQuickMirror"
        pie.operator("basti.linear_array")
        pie.operator("basti.scatter_duplicate")


class VIEW3D_MT_BastiQuickMirror(bpy.types.Menu):
    bl_label = "Quick Mirror"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for axis in ["X", "Y", "Z"]:
            op = col.operator("basti.quick_mirror", text=axis)
            op.axis = axis
            op.pivot = "ORIGIN"
            op.scope = "ISLAND"
            op.delete_target = "ISLAND"
            op.auto_merge = True


class VIEW3D_MT_BastiScaleToZero(bpy.types.Menu):
    bl_label = "Scale to Zero"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for axis in ["X", "Y", "Z"]:
            op = col.operator("basti.scale_to_zero", text=axis)
            op.axis = axis


class VIEW3D_MT_BastiMoveToZero(bpy.types.Menu):
    bl_label = "Move to Zero"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for key, settings in {
            "ALL": (True, True, True),
            "X": (True, False, False),
            "Y": (False, True, False),
            "Z": (False, False, True),
            "XY": (True, True, False),
            "XZ": (True, False, True),
            "YZ": (False, True, True),
        }.items():
            op = col.operator("basti.move_to_zero", text=key)
            op.x, op.y, op.z = settings
