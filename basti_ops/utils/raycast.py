import bpy

def raycast(
    context, coords
) -> tuple[bool, list[float], list[float], int, bpy.types.Object]:
    """Casts a ray at the mouse position and returns raycast_result, location, normal, face_index, obj_target"""
    from bpy_extras import view3d_utils

    scene = context.scene
    region = context.region
    rv3d = context.region_data
    depsgraph = bpy.context.evaluated_depsgraph_get()

    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coords)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coords)

    raycast_result, location, normal, polygon_index, obj_target, _ = scene.ray_cast(
        depsgraph, ray_origin, view_vector
    )
    return raycast_result, location, normal, polygon_index, obj_target