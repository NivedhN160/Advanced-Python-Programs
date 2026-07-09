import cv2
import tkinter as tk
from tkinter import filedialog

# Set up Tkinter and hide the main window
root = tk.Tk()
root.withdraw()

# 1. Open a file dialog to select an image from disk
file_path = filedialog.askopenfilename(
    title="Select an Image",
    filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
)

if file_path:
    # 2. Read the selected image
    img = cv2.imread(file_path)

    if img is not None:
        # 3. Display the image in a window titled "Preview Window"
        cv2.imshow('Preview Window', img)

        # 4. Keep the window open until ANY keyboard key is pressed
        cv2.waitKey(0)

        # 5. Clean up and close the GUI window safely
        cv2.destroyAllWindows()
    else:
        print("Error: Could not read the image.")
else:
    print("No file was selected.")
