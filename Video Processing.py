import cv2 as cv
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Hide the Tkinter root window
Tk().withdraw()

# Open file dialog to select a video
video_path = askopenfilename(
    title="Select a Video File",
    filetypes=[
        ("Video Files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
        ("All Files", "*.*")
    ]
)

# Check if a file was selected
if not video_path:
    print("No video file selected.")
    exit()

# Create output folder
output_dir = r"E:\College\Sem 5\Adv Python\programs\video processed"
os.makedirs(output_dir, exist_ok=True)

# Open the selected video
cap = cv.VideoCapture(video_path)

# Check if the video opened successfully
if not cap.isOpened():
    print("Error: Unable to open the video file.")
    exit()

frame_no = 0

# Extract frames
while True:
    ret, frame = cap.read()

    if not ret:
        break

    filename = os.path.join(output_dir, f"frame_{frame_no:05d}.jpg")
    cv.imwrite(filename, frame)

    frame_no += 1

# Release the video object
cap.release()

print(f"Total frames extracted: {frame_no}")
print(f"Frames saved in folder: {output_dir}")

