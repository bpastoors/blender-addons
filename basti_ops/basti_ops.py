import bpy

from .operators.copy_to_clipboard import BastiCopyToClipboard
from .operators.copy_to_mesh import BastiCopyToMesh
from .operators.paste_from_clipboard import BastiPasteFromClipboard
from .operators.radial_array import BastiRadialArray
from .operators.apply_material import BastiApplyMaterial
from .operators.bevel import BastiBevel
from .operators.move_to_face import BastiMoveToFace
from .operators.scale_to_zero import BastiScaleToZero
from .operators.move_to_zero import BastiMoveToZero
from .operators.delete import BastiDelete
from .operators.loop_slice import BastiLoopSlice
from .operators.set_selection_mode import BastiSetSelectionMode
from .operators.select_edge_or_island import BastiSelectEdgeOrIsland
from .operators.select_loop import BastiSelectLoop
from .operators.set_viewpoint import BastiSetViewpoint
from .operators.quick_mirror import BastiQuickMirror
from .operators.make_face import BastiMakeFace
from .operators.connect_or_knife import BastiConnectOrKnife
from .operators.toggle_sculpt_automasking import BastiToggleSculptAutomasking


classes = [
    BastiCopyToMesh,
    BastiCopyToClipboard,
    BastiPasteFromClipboard,
    BastiMoveToFace,
    BastiApplyMaterial,
    BastiSetSelectionMode,
    BastiBevel,
    BastiRadialArray,
    BastiSelectEdgeOrIsland,
    BastiSelectLoop,
    BastiScaleToZero,
    BastiMoveToZero,
    BastiDelete,
    BastiSetViewpoint,
    BastiLoopSlice,
    BastiQuickMirror,
    BastiMakeFace,
    BastiConnectOrKnife,
    BastiToggleSculptAutomasking,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
