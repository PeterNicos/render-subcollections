bl_info = {
    "name": "Render Subcollections",
    "author": "Nico",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "3D View > N-Panel > Render Subcollections",
    "description": "Choose a Collection, then leave the Add-On to activate individual collections within and render cameras inside these collections one after another.",
    "category": "Render"
}

import bpy
import os

# -------------------------------------------------------------
# Helpers
# -------------------------------------------------------------

def get_subcollections(collection, result=None):
    if result is None:
        result = []
    for child in collection.children:
        result.append(child)
        get_subcollections(child, result)
    return result


def find_layer_collection(layer_collection, target_collection):
    if layer_collection.collection == target_collection:
        return layer_collection
    for child in layer_collection.children:
        found = find_layer_collection(child, target_collection)
        if found:
            return found
    return None


# -------------------------------------------------------------
# Operators
# -------------------------------------------------------------

class RENDER_OT_selected_subcollections(bpy.types.Operator):
    """Render cameras in selected subcollections"""
    bl_idname = "render.selected_subcollections"
    bl_label = "Render Selected Subcollections"

    def execute(self, context):
        scene = context.scene

        # Store original output path
        original_path = scene.render.filepath

        # Output folder from Blender-Settings
        output_folder = bpy.path.abspath(original_path)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Main Collection containing all desired subcollections from dropdown
        main_collection = scene.main_collection
        if not main_collection:
            self.report({'WARNING'}, "No main collection selected!")
            return {'CANCELLED'}

        # Find all collections, selected in the panel
        subcollections = get_subcollections(main_collection)
        selected_collections = [col for col in subcollections if col.render_selected]

        if not selected_collections:
            self.report({'WARNING'}, "No subcollections selected!")
            return {'CANCELLED'}

        for collection in selected_collections:
            layer_col = find_layer_collection(bpy.context.view_layer.layer_collection, collection)
            if not layer_col:
                self.report({'WARNING'}, f"LayerCollection for {collection.name} not found!")
                continue

            # Activate temporarily
            original_state = layer_col.exclude
            layer_col.exclude = False

            # Cameras inside this specific collection
            cameras = [obj for obj in collection.objects if obj.type == 'CAMERA']
            if not cameras:
                self.report({'INFO'}, f"No camera in {collection.name}")
                layer_col.exclude = original_state
                continue

            for cam in cameras:
                scene.camera = cam

                # Filename = Prefix + Cameraname + Suffix
                prefix = scene.filename_prefix or ""
                suffix = scene.filename_suffix or ""
                filename = f"{prefix}{cam.name}{suffix}.png"
                
                filepath = os.path.join(output_folder, filename)

                # Set temporarily
                scene.render.filepath = filepath

                # Render
                bpy.ops.render.render(write_still=True)

                self.report({'INFO'}, f"Rendered: {filepath}")

            # Deactivate again
            layer_col.exclude = original_state

        # Restore Outputpath
        scene.render.filepath = original_path

        self.report({'INFO'}, "All renderings completed!")
        return {'FINISHED'}

    
class RENDER_OT_active_camera(bpy.types.Operator):
    """Render the currently active camera"""
    bl_idname = "render.active_camera"
    bl_label = "Render currently active Camera"

    def execute(self, context):
        scene = context.scene
        cam = scene.camera

        if cam is None:
            self.report({'WARNING'}, "No active camera set!")
            return {'CANCELLED'}

        # Store original output path
        original_path = scene.render.filepath

        # Output folder from Blender-Settings
        output_folder = bpy.path.abspath(original_path)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Filename = Prefix + Cameraname + Suffix
        prefix = scene.filename_prefix or ""
        suffix = scene.filename_suffix or ""
        filename = f"{prefix}{cam.name}{suffix}.png"

        filepath = os.path.join(output_folder, filename)

        # Set temporarily
        scene.render.filepath = filepath

        # Render
        bpy.ops.render.render(write_still=True)

        # Restore Outputpath
        scene.render.filepath = original_path

        self.report({'INFO'}, f"Rendered: {filepath}")
        return {'FINISHED'}




# -------------------------------------------------------------
# Panel (N-Panel)
# -------------------------------------------------------------

class RENDER_PT_subcollections(bpy.types.Panel):
    bl_label = "Render Subcollections"
    bl_idname = "RENDER_PT_subcollections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Render Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "main_collection", text="Main Collection")

        main_collection = scene.main_collection
        if main_collection:
            layout.label(text="Subcollections:")
            for col in get_subcollections(main_collection):
                row = layout.row()
                row.prop(col, "render_selected", text=col.name)

        layout.separator()
        layout.label(text="Filename Options", icon="FILE")

        row = layout.row()
        row.prop(scene, "filename_prefix", text="Prefix")

        row = layout.row()
        row.prop(scene, "filename_suffix", text="Suffix")


        layout.operator("render.selected_subcollections", text="Render Selected Subcollections")
        
        # Button to render active camera with name of the camera as filename
        layout.separator()  # kleiner Trenner
        layout.operator("render.active_camera", text="Render currently active Camera")


        # --- Output Settings ---
        layout.separator()
        layout.label(text="Output Settings", icon="OUTPUT")

        render = scene.render
        image_settings = render.image_settings

        box = layout.box()
        box.prop(render, "filepath", text="Output Path")
        box.prop(render, "use_file_extension")
        box.prop(render, "use_overwrite")
        box.prop(render, "use_placeholder")
        box.prop(render, "use_render_cache")

        # --- Resolution Settings ---
        layout.separator()
        layout.label(text="Resolution", icon="FULLSCREEN_ENTER")

        render = scene.render
        box = layout.box()
        row = box.row(align=True)
        row.prop(render, "resolution_x", text="X")
        row.prop(render, "resolution_y", text="Y")

        box.prop(render, "resolution_percentage", text="Scale (%)")

        # --- Format Settings ---
        layout.separator()
        layout.label(text="Format Settings", icon="FILE_IMAGE")

        box = layout.box()
        box.prop(image_settings, "file_format", text="Format")

        # Only show, when format supports color selection
        if image_settings.file_format not in {"OPEN_EXR", "HDR"}:
            box.prop(image_settings, "color_mode", text="Color Mode")

        # Color depth (if supported)
        if image_settings.file_format in {"PNG", "OPEN_EXR", "JPEG2000"}:
            box.prop(image_settings, "color_depth", text="Color Depth")

        # Compression (if supported)
        if image_settings.file_format in {"PNG", "JPEG", "JPEG2000"}:
            box.prop(image_settings, "compression", text="Compression")



# -------------------------------------------------------------
# Register
# -------------------------------------------------------------

classes = (
    RENDER_OT_selected_subcollections,
    RENDER_OT_active_camera,
    RENDER_PT_subcollections,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.main_collection = bpy.props.PointerProperty(
        name="Main Collection",
        description="Choose your Main Collection",
        type=bpy.types.Collection
    )

    bpy.types.Collection.render_selected = bpy.props.BoolProperty(
        name="Render",
        description="Render this collection?",
        default=False
    )

    bpy.types.Scene.filename_prefix = bpy.props.StringProperty(
        name="Prefix",
        description="Text that will be added in front of each cameraname"
    )

    bpy.types.Scene.filename_suffix = bpy.props.StringProperty(
        name="Suffix",
        description="Text that will be added after each cameraname"
    )




def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.main_collection_name
    del bpy.types.Collection.render_selected

    del bpy.types.Scene.filename_prefix
    del bpy.types.Scene.filename_suffix



if __name__ == "__main__":
    register()
