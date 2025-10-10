import bpy

class VIEW3D_MT_BastiCreateAndCenter(bpy.types.Menu):
    bl_label = "Create and Center"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("mesh.primitive_plane_add")
        pie.operator("mesh.primitive_cube_add")
        pie.operator("mesh.primitive_cylinder_add")
        pie.operator("mesh.primitive_uv_sphere_add")
        op = pie.operator("wm.call_menu", text="Scale to zero")
        op.name = "VIEW3D_MT_BastiScaleToZero"
        op = pie.operator("wm.call_menu", text="Move to zero")
        op.name = "VIEW3D_MT_BastiMoveToZero"
        op = pie.operator("wm.call_menu_pie", text="Duplicate")
        op.name = "VIEW3D_MT_BastiDuplicate"
        op = pie.operator("wm.call_menu_pie", text="Duplicate2")
        op.name = "VIEW3D_MT_BastiDuplicate"

class VIEW3D_MT_BastiDuplicate(bpy.types.Menu):
    bl_label = "Duplicate"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("basti.radial_array")

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

classes = [
    VIEW3D_MT_BastiCreateAndCenter,
    VIEW3D_MT_BastiDuplicate,
    VIEW3D_MT_BastiScaleToZero,
    VIEW3D_MT_BastiMoveToZero,
    VIEW3D_MT_BastiModeling
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)