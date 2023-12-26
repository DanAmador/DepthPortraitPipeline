import bpy
import json
from pathlib import Path

def get_camera_params(camera):
    params = {
        "fl_x": camera.lens,
        "fl_y": camera.lens,
        "cx": camera.sensor_width / 2,
        "cy": camera.sensor_height / 2,
        "w": bpy.context.scene.render.resolution_x,
        "h": bpy.context.scene.render.resolution_y,
        "frames": []
    }
    return params

def get_transform_matrix(camera_obj):
    return [list(row) for row in camera_obj.matrix_world]

def update_json_file(json_path, camera_params):
    with open(json_path, 'w') as json_file:
        json.dump(camera_params, json_file, indent=2)

def check_existing_frames(images_folder, json_path):
    # Check existing images with .png and .jpg extensions
    existing_images = sorted([img for img in images_folder.iterdir() if img.suffix in ['.png', '.jpg']])
    num_images = len(existing_images)

    # Check JSON file
    if json_path.exists():
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
            num_json_frames = len(data.get("frames", []))
            return min(num_images, num_json_frames)
    return 0

def render_next_frame():
    global frame_index, camera_params, images_folder, base_output_path
    print(frame_index / end_frame)
    if frame_index > end_frame:
        # Finish rendering
        bpy.app.timers.unregister(render_next_frame)
        bpy.context.scene.render.filepath = str(base_output_path)
        print("Finished rendering animation.")
        return None

    scene = bpy.context.scene
    scene.frame_set(frame_index)
    image_path = images_folder / f"image_{frame_index:04d}.png"  # Assuming PNG format for new renders
    scene.render.filepath = str(image_path)
    bpy.ops.render.render(write_still=True)

    camera_params["frames"].append({
        "file_path": str(image_path.relative_to(base_output_path)),
        "transform_matrix": get_transform_matrix(scene.camera)
    })

    # Update JSON file after each frame
    json_path = base_output_path / "transforms.json"
    update_json_file(json_path, camera_params)

    frame_index += 1
    return 0.1  # Time in seconds before the next call (adjust as needed)

# Main script
base_output_path = Path(bpy.context.scene.render.filepath)

# Ensure the path ends with a separator
if not base_output_path.name:
    base_output_path = base_output_path.parent

# Create an 'images' subfolder
images_folder = base_output_path / "images"
images_folder.mkdir(parents=True, exist_ok=True)
global frame_index
# Check for existing frames
json_path = base_output_path / "transforms.json"
frame_index = check_existing_frames(images_folder, json_path)
print(f"Existing frames: {frame_index}")
start_frame = bpy.context.scene.frame_start
end_frame = bpy.context.scene.frame_end
camera = bpy.context.scene.camera.data
camera_params = get_camera_params(camera)

if frame_index == 0:
    frame_index = start_frame

# Start rendering with a timer
bpy.app.timers.register(render_next_frame)
