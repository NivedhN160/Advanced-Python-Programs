import cv2
import os
import glob

# Set the path to the folder containing frames
frames_dir = r"E:\College\Sem 5\Adv Python\programs\video processed"

# Get all frame files and sort them to maintain correct order
frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.jpg")))

if not frame_files:
    print("No frames found in the specified directory.")
    exit()

print(f"Playing {len(frame_files)} frames...")

# Frame rate configuration
fps = 30
delay = int(1000 / fps)

for frame_path in frame_files:
    img = cv2.imread(frame_path)
    if img is not None:
        cv2.imshow("Playing Image Frames as Video", img)
    
    # Wait for the calculated delay, exit if 'q' is pressed
    if cv2.waitKey(delay) & 0xFF == ord('q'):
        print("Playback stopped by user.")
        break

cv2.destroyAllWindows()
print("Playback finished.")
