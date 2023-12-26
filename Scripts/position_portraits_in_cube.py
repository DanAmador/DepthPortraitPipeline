import bpy
from mathutils import Vector

# Define the size of the virtual cube (assuming it's centered at the world origin)
cube_size = 4.0  # This represents the edge length of the cube

# Get the parent collection containing the nested collections
parent_collection_name = "Portraits"
parent_collection = bpy.data.collections[parent_collection_name]

# Calculate the half size (for centering purposes)
half_size = cube_size / 2

# Define the centers of the cube faces
face_centers = [
    Vector((0, 0, half_size)),   # Top face center
    Vector((0, 0, -half_size)),  # Bottom face center
    Vector((half_size, 0, 0)),   # Front face center
    Vector((-half_size, 0, 0)),  # Back face center
    Vector((0, half_size, 0)),   # Right face center
    Vector((0, -half_size, 0)),  # Left face center
]

# Define the normals of the cube faces
face_normals = [
    Vector((0, 0, 1)),   # Top face normal
    Vector((0, 0, -1)),  # Bottom face normal
    Vector((1, 0, 0)),   # Front face normal
    Vector((-1, 0, 0)),  # Back face normal
    Vector((0, 1, 0)),   # Right face normal
    Vector((0, -1, 0)),  # Left face normal
]

# Make sure we have the same number of nested collections as cube faces
nested_collections = [col for col in parent_collection.children]
if len(nested_collections) != 6:
    raise ValueError("The parent collection must contain exactly 6 nested collections.")

# Function to calculate the scale factor for an object
def calc_scale_factor(obj, target_size):
    # Calculate the scale factor based on the object's bounding box dimensions
    dimensions = obj.dimensions
    max_dimension = max(dimensions)
    scale_factor = target_size / max_dimension
    print(f"Scale factor: {scale_factor} for {obj.name}")
    return scale_factor

# Function to position, scale, and rotate objects in a collection
def position_and_scale_collection_objects(col, center, normal, target_size):
    for obj in col.objects:
        # Calculate scale factor
        obj.scale = ( 1,1 ,1)
        scale_factor = calc_scale_factor(obj, target_size / 2)
        
        # Move the object to the face center
        obj.location = center
        
        # Scale the object
        obj.scale = (scale_factor, scale_factor, scale_factor)
        
        # Rotate the object to align with the face normal
        obj.rotation_euler = normal.to_track_quat('Z', 'Y').to_euler()

# Iterate over each nested collection and position its objects
for nested_col, center, normal in zip(nested_collections, face_centers, face_normals):
    position_and_scale_collection_objects(nested_col, center, normal, cube_size )

# Update the scene
bpy.context.view_layer.update()
