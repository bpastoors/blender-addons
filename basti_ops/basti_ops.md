# Basti's Operators

### .apply_material
Apply the material pointed at with the mouse cursor to the selection. Material can be sampled the same or a different mesh.  
Pointing at nothing creates and applies a new material.

### .bevel
Launch the appropriate bevel tool for the current selection mode.  
A face selection activates the extrude tool. 

### .connect_or_knife
Create an edge between two selected vertices or launch the knife tool.

### .copy_to_clipboard
Copy the selected mesh elements to the clipboard.
* **cut:** delete selected elements - cutting instead of copying

### .copy_to_mesh
Copy the selected mesh elements to the mesh pointed at with the mouse cursor. The targeted mesh can be the same as the source mesh.  
Pointing at nothing copy into a new mesh object.
* **cut:** delete selected elements - cutting instead of copying

### .delete
Execute the appropriate deletion based on the selection mode without popping up the deletion dialog.
* **Dissolve:** dissolve selected elements instead

### .linear_array
Create a line or grid of copies of the selection.
* **count:** how many copies to add
* **offset:** the offsets between copies
* **between:** distribute copies evenly in the offset
* **islands:** when in edit mode duplicate the whole mesh island instead of just the selection
* **linked:** when in object mode duplicate duplicate the objects linked to the same data

### .loop_slice
Get the edge ring or face loop based on the selection and subdivide them. Then enter the edge sliding tool if only one edge has been added.
* **Multi:** whether to add one edge and slide it or add multiple
* **Count:** how many edges to add in multi-mode

### .make_face
Create new faces based on the selection.  
When exactly two adjacent edges or three vertices are selected a triangle is created. Or border edges are found based on the selection and holes filled. 


### .merge_by_type
Execute the merge operator to collapse Edges and Faces and merge Vertices at Center.
* **Override Mode:** select a different merging mode


### .move_to_face
Move the selected object or mesh island to the point on a face pointing at with the mouse. Can target the same or other meshes.  
When in edit mode, not just the selection, but all linked elements will be moved.
* **orient:** in object mode the object can be rotated to align with the face normal
* **spin:** spin around the normal that you oriented to

### .move_to_zero
Move the selection to zero on the selected axis in world-space.
* **X:** move to zero on X axis 
* **Y:** move to zero on Y axis 
* **Z:** move to zero on Z axis 

### .paste_from_clipboard
Paste elements copied with **.copy_to_clipboard** into the currently selected mesh
* **cleanup_materials:** matches materials on the pasted polygons to materials in the scene by name to avoid duplicates  


### .quick_mirror
Mirror geometry across an axis, with the option to clear geometry on the target side first.  
The source side is determined by where the selection is in relation to the pivot.
* **Axis:** the axis to mirror on 
* **Pivot:** the pivot to mirror across 
* **Scope:** mirror only selected, everything linked to the selected or everything on the same side of the pivot
* **Delete Target Side:** whether to not delete anything, only elements linked to the selection or everything on the other side of the pivot
* **Automatic Merge:** doing a "merge by distance" on vertices after the mirror operation
* **Automatic Merge Distance:** the distance threshold for the automatic merging

### .radial_array
Create a ring of copies of the selection.
* **pivot:** the pivot to rotate around
* **axis:** the axis to rotate around
* **count:** how many copies to add
* **islands:** when in edit mode duplicate the whole mesh island instead of just the selection
* **linked:** when in object mode duplicate duplicate the objects linked to the same data

### .rotate_to_zero
Rotate the submesh so that the face selection is aligned with an axis
* **axis:** the axis to align with
* **flip:** flip the direction of the target axis
* **spin:** spin the submesh around the axis 

### .scale_to_zero
Scale selection to zero on an axis
* **axis:** the axis to scale on

### .scatter_duplicate
Create copies of the selection with randomized offsets and rotations
* **count:** how many copies to add
* **offset:** the maximum offset
* **add_negative_offset:** instead of random values between 0 and maximum, extend the range to -maximum to maximum
* **rotation:** the maximum rotation in degrees
* **add_negative_rotation:** instead of random values between 0 and maximum, extend the range to -maximum to maximum
* **seed:** the seed for randomization
* **islands:** when in edit mode duplicate the whole mesh island instead of just the selection
* **linked:** when in object mode duplicate duplicate the objects linked to the same data

### .select_edge_or_island
Select the edge loop when in edge mode or the mesh island otherwise.

### .select_loop
Select edge loops when in edge or vertex mode or face loops when in face mode.  
Define face loops by selecting two adjoining faces.

### .set_action_center
Set the transform pivot and orientation based on action center presets.
* **action_center:** the preset to set

### .set_cursor
Set the location and rotation of the cursor.  
Origin and Pivot always work as expected, Selection and Pivot work with objects or elements in edit mode.
* **target:** what to snap the cursor to

### .set_selection_mode
Set the selection mode and toggle between object and edit mode accordingly.
* **selection mode:** the mode to switch to

### .set_viewpoint
Set the view axis and toggle between orthographic and perspective view. All directions are orthographic
* **viewpoint:** the viewpoint to switch to

### .toggle_sculpt_automasking
Toggle sculpt automasking on or off.
* **Mode:** the type of automasking to toggle




# Basti's Menus



# Basti's Panels