import bmesh
import bpy
from mathutils import Vector

from ..utils.object import duplicate_object
from ..utils.selection import (
    select_by_id,
    get_mesh_selection_mode,
    get_selected_bm_vertices,
    set_mesh_selection_mode,
    get_linked_verts,
)
from ..utils.mesh import duplicate_bmesh_geometry


class BastiLinearArray(bpy.types.Operator):
    """.linear_array
    Create a line or grid of copies of the selection.
    * count: how many copies to add
    * offset: the offsets between copies
    * between: distribute copies evenly in the offset
    * islands: when in edit mode duplicate the whole mesh island instead of just the selection
    * linked: when in object mode duplicate the objects linked to the same data
    """

    bl_idname = "basti.linear_array"
    bl_label = "Linear Array"
    bl_options = {"REGISTER", "UNDO"}

    count: bpy.props.IntVectorProperty(default=(1, 1, 1))
    offset: bpy.props.FloatVectorProperty()
    between: bpy.props.BoolProperty(default=False)
    islands: bpy.props.BoolProperty(default=False)
    linked: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None and context.active_object.type == "MESH"
        )

    def execute(self, context):
        selection_mode = get_mesh_selection_mode(context)
        active_object = context.active_object
        offset = [0.0, 0.0, 0.0]
        for axis in range(0, 3):
            offset[axis] = (
                self.offset[axis] / self.count[axis] - 1
                if self.between and self.count[axis] > 1
                else self.offset[axis]
            )

        if selection_mode == "OBJECT":
            objs_to_duplicate = [active_object]
            for axis in range(0, 3):
                if offset[axis] != 0:
                    new_offset = [0.0, 0.0, 0.0]
                    new_objs = []
                    for i in range(1, self.count[axis]):
                        new_offset[axis] = offset[axis] * i

                        for obj in objs_to_duplicate:
                            new_obj = duplicate_object(obj, self.linked)
                            new_obj.location = new_obj.location + Vector(new_offset)
                            new_objs.append(new_obj)

                    objs_to_duplicate.extend(new_objs)

            return {"FINISHED"}

        bm = bmesh.from_edit_mesh(active_object.data)
        selected_verts = get_selected_bm_vertices(bm, active_object)
        if self.islands:
            selected_verts = get_linked_verts(active_object, bm, selected_verts)

        for axis in range(0, 3):
            if offset[axis] != 0:
                new_offset = [0.0, 0.0, 0.0]
                vert_selection_extension = []

                for i in range(1, self.count[axis]):
                    new_offset[axis] = offset[axis] * i
                    new_verts = duplicate_bmesh_geometry(bm, selected_verts)
                    for vert in new_verts:
                        vert.co += Vector(new_offset)
                    vert_selection_extension.extend(new_verts)

                selected_verts.extend(vert_selection_extension)

        vert_ids = [v.index for v in selected_verts]
        bmesh.update_edit_mesh(active_object.data)

        set_mesh_selection_mode("OBJECT")
        select_by_id(active_object, "VERT", vert_ids)
        set_mesh_selection_mode("OBJECT")
        set_mesh_selection_mode(selection_mode)
        bm.free()
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "count")
        layout.prop(self, "offset")
        layout.prop(self, "between")

        selection_mode = get_mesh_selection_mode(context)
        if selection_mode == "OBJECT":
            layout.prop(self, "linked")
        else:
            layout.prop(self, "islands")
