import cv2
import uuid
import subprocess
import platform

def get_camera_info():
    # Get platform information
    system = platform.system()
    if system == "Windows":
        command = "wmic path Win32_PnPEntity WHERE \"Caption LIKE '%Camera%'\" get DeviceID"
    elif system == "Linux":
        command = "ls /dev/video*"
    else:
        raise NotImplementedError("Platform not supported")

    # Execute shell command to get camera information
    output = subprocess.check_output(command, shell=True)
    cameras = output.decode().split('\n')

    # Filter out empty strings and return camera names
    camera_paths = [path.strip() for path in cameras if path.strip()]
    return camera_paths

def test_webcams():
    # Get the list of available cameras
    camera_paths = get_camera_info()
    num_cameras = len(camera_paths)

    print("Number of cameras detected:", num_cameras)

    # Assign IDs to each camera
    camera_ids = {}
    for camera_path in camera_paths:
        camera_id = uuid.uuid5(uuid.NAMESPACE_OID, camera_path).hex  # Generate a UUID for the camera using SHA-1 hash of the device path
        camera_ids[camera_path] = camera_id

    print("Camera IDs:", camera_ids)

    # Test each camera
    for camera_path, camera_id in camera_ids.items():
        cap = cv2.VideoCapture(camera_path)
        if not cap.isOpened():
            continue
        
        print("Testing Camera", camera_path, "with ID:", camera_id)
        
        # Capture a frame
        ret, frame = cap.read()
        if ret:
            # Display the frame
            cv2.imshow("Camera " + str(camera_path), frame)
            cv2.waitKey(1000)  # Display each camera feed for 1 second

        # Release the camera
        cap.release()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_webcams()