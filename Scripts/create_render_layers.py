import bpy

# Name of the view layer to keep
background_layer_name = "Background"

# Iterate over the list of view layers and remove the ones not matching 'keep_layer_name'
for view_layer in bpy.context.scene.view_layers[:]:  # Make a copy of the list to iterate over
    if view_layer.name != background_layer_name:
        bpy.context.scene.view_layers.remove(view_layer)
        
def create_compositing_layers():
    # Enable use nodes in compositor
    bpy.context.scene.use_nodes = True
    node_tree = bpy.context.scene.node_tree

    # Clear existing nodes
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)

    # Create a render layers node for each view layer and a composite node
    render_layers_nodes = []
    for view_layer in bpy.context.scene.view_layers:
        render_node = node_tree.nodes.new('CompositorNodeRLayers')
        render_node.layer = view_layer.name
        render_layers_nodes.append(render_node)

# Create a composite node
    composite_node = node_tree.nodes.new('CompositorNodeComposite')
    composite_node.location = 400, 0

    # Link render layers to composite node through additive mix nodes
    previous_node = None
    for node in render_layers_nodes:
        if previous_node is None:
            previous_node = node
        else:
            # Create a mix node and set up its location
            mix_node = node_tree.nodes.new('CompositorNodeMixRGB')
            mix_node.blend_type = 'MIX'  # Using standard mix
            mix_node.location = previous_node.location.x + 200, previous_node.location.y
            
            # Use the alpha channel of the current layer as the mix factor
            node_tree.links.new(node.outputs['Alpha'], mix_node.inputs[0])

            # Link the nodes
            node_tree.links.new(previous_node.outputs[0], mix_node.inputs[1])
            node_tree.links.new(node.outputs[0], mix_node.inputs[2])
            
            previous_node = mix_node
    # Connect the last node to the composite node
    if previous_node:
        node_tree.links.new(previous_node.outputs[0], composite_node.inputs[0])

def create_view_layers_for_collections(parent_collection_name):
    parent_collection = bpy.data.collections.get(parent_collection_name)

    if parent_collection is not None:
        # Clear existing view layers except the original one
        for view_layer in bpy.context.scene.view_layers[:]:
            if view_layer.name != bpy.context.view_layer.name and view_layer.name != background_layer_name:
                bpy.context.scene.view_layers.remove(view_layer)

        # Check if 'Non-Portraits' view layer exists, if not, create it
        if not any(view_layer.name ==  background_layer_name for view_layer in bpy.context.scene.view_layers):
            other_layer = bpy.context.scene.view_layers.new(name=background_layer_name)
        else:
            other_layer = bpy.context.scene.view_layers[background_layer_name]

        # Configure the 'Non-Portraits' layer
        
        for layer_collection in other_layer.layer_collection.children:
            print(layer_collection.name, parent_collection.name)
            # Exclude all collections inside the parent collection
            if layer_collection.name == parent_collection.name:
                for child_layer in layer_collection.children:
                    child_layer.exclude = True
            else:
                layer_collection.exclude = layer_collection.name not in [child.name for child in parent_collection.children]

        # Create view layers for each child collection
        for child_collection in parent_collection.children:
            new_view_layer = bpy.context.scene.view_layers.new(name=child_collection.name)
            
            # Exclude everything in the new view layer initially
            def exclude_all_collections(layer_collection):
                layer_collection.exclude = True
                for child_layer in layer_collection.children:
                    exclude_all_collections(child_layer)
            


            # Include only the current child collection
            def include_collection(layer_collection, collection_name):
                if layer_collection.name == collection_name:
                    layer_collection.exclude = False
                for child_layer in layer_collection.children:
                    include_collection(child_layer, collection_name)
            


            exclude_all_collections(new_view_layer.layer_collection)
            include_collection(new_view_layer.layer_collection, child_collection.name)
            include_collection(other_layer.layer_collection, background_layer_name)

create_view_layers_for_collections("Portraits")
create_compositing_layers()

print("View layers and node graph setup complete.")