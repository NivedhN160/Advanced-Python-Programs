'''
OpenCV's VideoCapture capture properties and Usages:
OpenCV's VideoCapture class provides several capture properties that allow you to retrieve information about a video or camera and, in some cases, modify its settings. These properties are accessed using:
Get a property
value = cap.get(property_name)
Set a property
cap.set(property_name, value)
Common VideoCapture Properties
Property
Description
Example Usage
cv.CAP_PROP_POS_MSEC
Current position in milliseconds
Jump to or retrieve the current timestamp in a video.
cv.CAP_PROP_POS_FRAMES
Current frame number
Read or move to a specific frame.
cv.CAP_PROP_POS_AVI_RATIO
Relative position (0.0–1.0)
Jump to the middle or end of a video.
cv.CAP_PROP_FRAME_WIDTH
Width of the video frame
Get or set frame width.
cv.CAP_PROP_FRAME_HEIGHT
Height of the video frame
Get or set frame height.
cv.CAP_PROP_FPS
Frames per second
Determine the video's frame rate.
cv.CAP_PROP_FRAME_COUNT
Total number of frames
Calculate video duration or iterate through all frames.
cv.CAP_PROP_FOURCC
Video codec
Identify the codec used for the video.
cv.CAP_PROP_BRIGHTNESS
Camera brightness
Adjust webcam brightness (if supported).
cv.CAP_PROP_CONTRAST
Camera contrast
Change webcam contrast.
cv.CAP_PROP_SATURATION
Camera saturation
Adjust color intensity.
cv.CAP_PROP_HUE
Camera hue
Modify the color tone.
cv.CAP_PROP_GAIN
Camera gain
Increase or decrease signal amplification.
cv.CAP_PROP_EXPOSURE
Camera exposure
Adjust image exposure for webcams.
cv.CAP_PROP_AUTO_EXPOSURE
Automatic exposure
Enable or disable auto exposure.
cv.CAP_PROP_AUTOFOCUS
Autofocus mode
Enable or disable autofocus.
cv.CAP_PROP_FOCUS
Manual focus
Set the focus value manually (supported cameras only).
cv.CAP_PROP_ZOOM
Camera zoom
Control optical/digital zoom if supported.
cv.CAP_PROP_BUFFERSIZE
Capture buffer size
Reduce latency in live video streams.


Examples
1. Get Video Resolution
import cv2 as cv

cap = cv.VideoCapture("video.mp4")

width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)

print("Width :", width)
print("Height:", height)

cap.release()
Output
Width : 1920.0
Height: 1080.0

2. Get Frame Rate (FPS)
import cv2 as cv

cap = cv.VideoCapture("video.mp4")

fps = cap.get(cv.CAP_PROP_FPS)
print("FPS:", fps)

cap.release()
Example Output
FPS: 30.0

3. Get Total Number of Frames
import cv2 as cv

cap = cv.VideoCapture("video.mp4")

frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
print("Total Frames:", frames)

cap.release()

4. Calculate Video Duration
import cv2 as cv

cap = cv.VideoCapture("video.mp4")

fps = cap.get(cv.CAP_PROP_FPS)
frames = cap.get(cv.CAP_PROP_FRAME_COUNT)

duration = frames / fps

print("Duration:", duration, "seconds")

cap.release()

5. Jump to 10 Seconds
import cv2 as cv

cap = cv.VideoCapture("video.mp4")

cap.set(cv.CAP_PROP_POS_MSEC, 10000)

ret, frame = cap.read()

if ret:
    cv.imshow("10th Second", frame)
    cv.waitKey(0)

cap.release()
cv.destroyAllWindows()

6. Jump to the Middle of the Video
import cv2 as cv

cap = cv.VideoCapture("video.mp4")

cap.set(cv.CAP_PROP_POS_AVI_RATIO, 0.5)

ret, frame = cap.read()

if ret:
    cv.imshow("Middle Frame", frame)
    cv.waitKey(0)

cap.release()
cv.destroyAllWindows()

7. Set Webcam Resolution
import cv2 as cv

cap = cv.VideoCapture(0)

cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    cv.imshow("Webcam", frame)

    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()

8. Adjust Webcam Brightness
import cv2 as cv

cap = cv.VideoCapture(0)

cap.set(cv.CAP_PROP_BRIGHTNESS, 0.6)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    cv.imshow("Brightness", frame)

    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
Note: Brightness, contrast, exposure, focus, zoom, and similar camera controls are hardware-dependent. Many webcams ignore these settings.

Frequently Used Properties for Video Files
Property
Typical Use
CAP_PROP_FRAME_COUNT
Determine the total number of frames.
CAP_PROP_FPS
Calculate video duration and frame intervals.
CAP_PROP_FRAME_WIDTH
Get the width of each frame.
CAP_PROP_FRAME_HEIGHT
Get the height of each frame.
CAP_PROP_POS_FRAMES
Access a specific frame directly.
CAP_PROP_POS_MSEC
Seek to a specific timestamp.


Frequently Used Properties for Webcams
Property
Purpose
CAP_PROP_FRAME_WIDTH
Set capture resolution.
CAP_PROP_FRAME_HEIGHT
Set capture resolution.
CAP_PROP_FPS
Request a capture frame rate.
CAP_PROP_BRIGHTNESS
Adjust brightness.
CAP_PROP_CONTRAST
Adjust contrast.
CAP_PROP_EXPOSURE
Control exposure.
CAP_PROP_AUTOFOCUS
Enable or disable autofocus.
CAP_PROP_FOCUS
Set manual focus.

Summary
Use get() to retrieve information such as resolution, FPS, duration, or current position.
Use set() to change properties like playback position or camera settings.
Properties related to video files (frame count, FPS, position) are generally supported across platforms.
Properties related to camera hardware (brightness, exposure, focus, zoom, etc.) depend on the camera and its driver, so support varies by device and operating system.


'''

import cv2 as cv
from tkinter import Tk, filedialog

def main():
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Open a file dialog to select a video
    video_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[
            ("Video Files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
            ("All Files", "*.*")
        ]
    )

    if not video_path:
        print("No video file selected.")
        return

    print(f"Opening video: {video_path}")
    cap = cv.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Could not open the selected video file.")
        return
        
    print("\n--- 1 & 2 & 3 & 4. Getting Video Properties ---")
    width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv.CAP_PROP_FPS)
    frames = cap.get(cv.CAP_PROP_FRAME_COUNT)
    
    duration = frames / fps if fps > 0 else 0

    print("Width :", width)
    print("Height:", height)
    print("FPS:", fps)
    print("Total Frames:", int(frames))
    print(f"Duration: {duration:.2f} seconds")

    print("\n--- 5. Jump to 10 Seconds ---")
    cap.set(cv.CAP_PROP_POS_MSEC, 10000)
    ret, frame = cap.read()
    if ret:
        print("Successfully read frame at 10 seconds.")
        cv.imshow("10th Second - Press any key to continue", frame)
        cv.waitKey(0)
    else:
        print("Failed to read frame at 10 seconds (maybe video is shorter than 10s?).")
        
    # Close the window from the 10th second before opening the next
    cv.destroyAllWindows()

    print("\n--- 6. Jump to the Middle of the Video ---")
    cap.set(cv.CAP_PROP_POS_AVI_RATIO, 0.5)
    ret, frame = cap.read()
    if ret:
        print("Successfully read frame at the middle of the video.")
        cv.imshow("Middle Frame - Press any key to continue", frame)
        cv.waitKey(0)
    else:
        print("Failed to read frame at the middle.")
        
    cv.destroyAllWindows()

    print("\n--- 7 & 8. Hardware Properties (Resolution/Brightness) ---")
    print("Note: Setting resolution or brightness on a video file typically has no effect (unlike webcams).")
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv.CAP_PROP_BRIGHTNESS, 0.5)

    print("Attempted to set FRAME_WIDTH to 640. Current FRAME_WIDTH:", cap.get(cv.CAP_PROP_FRAME_WIDTH))
    print("Attempted to set FRAME_HEIGHT to 480. Current FRAME_HEIGHT:", cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    print("Attempted to set BRIGHTNESS to 0.5. Current BRIGHTNESS:", cap.get(cv.CAP_PROP_BRIGHTNESS))

    cap.release()
    print("\nFinished processing video.")

if __name__ == "__main__":
    main()