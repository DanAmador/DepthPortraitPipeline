import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty
from pathlib import Path
import math
class ImportDepthAndRGBFromFolder(Operator, ImportHelper):
    """Import Depth and RGB Images from a Folder and Setup Geometry Nodes"""
    bl_idname = "import_scene.depth_rgb_folder"
    bl_label = "Import Depth Portrait"
    bl_options = {'REGISTER', 'UNDO'}

    directory: StringProperty(
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default='',
        options={'HIDDEN'}
    )

    def execute(self, context):
        folder_path = Path(self.directory)

        depth_image_path, rgb_image_path = self.find_images(folder_path)
        if not depth_image_path:
            self.report({'ERROR'}, "No depth images found with prefix 'depth_'")
            return {'CANCELLED'}

        depth_image = bpy.data.images.load(str(depth_image_path))
        rgb_image = bpy.data.images.load(str(rgb_image_path)) if rgb_image_path else depth_image

        self.apply_geometry_nodes(folder_path.name, depth_image, rgb_image)

        return {'FINISHED'}

    def find_images(self, folder_path):
        depth_images = list(folder_path.glob('depth_*.png'))
        if not depth_images:
            return None, None

        depth_image_path = depth_images[0]
        name = depth_image_path.stem.split('depth_')[-1]
        rgb_image_path = folder_path / f'{name}.png'

        if not rgb_image_path.exists():
            rgb_image_path = None

        return depth_image_path, rgb_image_path

    def apply_geometry_nodes(self,name, depth_image, rgb_image ):
    # Create a new mesh and object
           # Create a new mesh and object
        object_name = f"{name} Portrait"
        mesh = bpy.data.meshes.new(name=object_name)
        obj = bpy.data.objects.new(f"{object_name} Mesh", mesh)
        
        # Rotate the object 90 degrees on the X-axis
        obj.rotation_euler[0] = math.radians(90)

        # Check if the "Portraits" collection exists
        portraits_collection = bpy.data.collections.get("Portraits")
        if not portraits_collection:
            # Optionally, create the "Portraits" collection if it doesn't exist
            portraits_collection = bpy.data.collections.new("Portraits")
            bpy.context.scene.collection.children.link(portraits_collection)

        # Create or get the specific collection for this object
        collection_name = f"{name} Collection"
        if collection_name not in bpy.data.collections:
            # Create a new collection if it doesn't exist
            new_collection = bpy.data.collections.new(collection_name)
            portraits_collection.children.link(new_collection)  # Add to "Portraits" collection
        else:
            # Get the existing collection
            new_collection = bpy.data.collections[collection_name]

        # Add the object to the new collection
        new_collection.objects.link(obj)
        
        # Link the object to the scene and set it as active
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        # Add Geometry Nodes modifier
        geo_nodes_modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
        procedural_box = bpy.data.node_groups.get("Procedural Box")
        if procedural_box:
            geo_nodes_modifier.node_group = procedural_box
        else:
            self.report({'ERROR'}, "Procedural Box node group not found")
            return {'CANCELLED'}

        # Assign images to node group inputs
        if procedural_box.nodes:
            group_input = next((node for node in procedural_box.nodes if node.type == 'GROUP_INPUT'), None)
            if group_input is not None:
                for input in group_input.outputs:
                    if input.name == "Depth":
                        obj.modifiers['GeometryNodes'][input.identifier] = depth_image
                    elif input.name == "RGB":
                        obj.modifiers['GeometryNodes'][input.identifier] = rgb_image

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(ImportDepthAndRGBFromFolder.bl_idname, text="Import Depth Portrait")

def register():
    bpy.utils.register_class(ImportDepthAndRGBFromFolder)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportDepthAndRGBFromFolder)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()