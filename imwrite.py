import cv2
import tkinter as tk
from tkinter import filedialog

# Set up Tkinter and hide the main window
root = tk.Tk()
root.withdraw()

# 1. Open a file dialog to select an image from disk (using imread)
input_path = filedialog.askopenfilename(
    title="Select an Image to Read",
    filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
)

if input_path:
    # 2. Read the selected image
    img = cv2.imread(input_path)

    if img is not None:
        # Let's convert the image to grayscale as a simple processing step before saving
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print("Image successfully loaded and converted to grayscale.")

        # 3. Open a file dialog to choose where to save the image
        output_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )

        if output_path:
            # 4. Save the modified image to disk using imwrite
            success = cv2.imwrite(output_path, gray_img)
            
            if success:
                print(f"Successfully saved image to {output_path}")
            else:
                print("Error: Could not save the image.")
        else:
            print("Save operation cancelled.")
    else:
        print("Error: Could not read the input image.")
else:
    print("No input file was selected.")
