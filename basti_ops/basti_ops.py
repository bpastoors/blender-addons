import bpy

from .ops_copying import BastiCopyToMesh, BastiCopyToClipboard, BastiPasteFromClipboard, BastiRadialArray
from .ops_material import BastiApplyMaterial
from .ops_modeling import BastiBevel, BastiMoveToFace, BastiMergeToActive
from .ops_selection import BastiSetSelectionMode

# class TraceSpriteToMesh(bpy.types.Operator):
#     bl_idname = "basti.trace_sprite"
#     bl_label = "Create a mesh based on the sprite"

#     @classmethod
#     def poll(cls, context):
#         return True

#     def execute(self, context):
#         image = bpy.data.images["FOX_head.png"]

#         image_size = image.size
#         pixels = list(image.pixels)
#         pixels_len = len(pixels)

#         pixel_alphas = [pixels[i] for i in range(3, pixels_len, 4)]

#         print(len(pixel_alphas))
#         print(image_size[0] * image_size[1])
#         return {'FINISHED'}


# class PlanarUV01(bpy.types.Operator):
#     bl_idname = "basti.planar_uv_01"
#     bl_label = "Planar uvs with set size"
#
#     @classmethod
#     def poll(cls, context):
#         return True
#
#     def execute(self, context):
#         mesh = bpy.context.active_object
#         mesh.data.uv_layers.new(name="spriteUV", do_init=False)
#
#         bm = bmesh.new()
#         bm.from_mesh(mesh.data)
#         uv_layer = bm.loops.layers.uv["spriteUV"]
#         for vert in bm.verts:
#             for loop in vert.link_loops:
#                 luv = loop[uv_layer]
#                 coords = vert.co.copy()
#                 luv.uv = (coords[0] + 0.5, coords[1] + 0.5)
#         bm.to_mesh(mesh.data)
#         bm.free()
#
#         return {"FINISHED"}


classes = [
    BastiCopyToMesh,
    BastiCopyToClipboard,
    BastiPasteFromClipboard,
    BastiMoveToFace,
    BastiApplyMaterial,
    BastiSetSelectionMode,
    BastiBevel,
    BastiMergeToActive,
    BastiRadialArray
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
