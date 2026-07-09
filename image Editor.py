'''
Develop a Python application using OpenCV and Tkinter to perform various image processing operations on a digital image. The application should provide a graphical user interface (GUI) that allows users to upload an image, apply image enhancement and transformation techniques through interactive sliders, preview the processed image in real time, and save the output image.

Functional Requirements:
Provide an option to upload an image from the local system.
Display the selected image in the application window.
Implement the following image processing operations using OpenCV:
Brightness Adjustment
Contrast Adjustment
Gaussian Blur
Image Rotation
Zoom In / Zoom Out
Image Sharpening
Saturation Adjustment
Hue Adjustment
Use sliders (trackbars) to control the parameters of each operation interactively.
Display the processed image in real time as the slider values change.
Provide a Reset option to restore the original image.
Provide a Save option to store the processed image in the desired format.
Design the GUI such that the image preview is displayed on the left side and all controls are placed on the right side in a scrollable panel.
Expected Outcome:
The application should function as a mini image editing studio capable of performing multiple image processing operations interactively and saving the final processed image.'''

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor Studio")
        self.root.geometry("1000x700")

        # Apply Windows XP Luna Aesthetic
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_color = "#ECE9D8" # Classic Luna Beige
        self.root.configure(bg=bg_color)
        
        style.configure('.', background=bg_color, font=('Tahoma', 9))
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color)
        style.configure('TLabelframe.Label', background=bg_color, font=('Tahoma', 9, 'bold'))
        style.configure('TLabel', background=bg_color)
        
        # Windows XP Colored Buttons
        style.configure('Upload.TButton', background="#316AC5", foreground="white", font=('Tahoma', 9, 'bold'), padding=5)
        style.map('Upload.TButton', background=[('active', '#4A84DF')])
        
        style.configure('Save.TButton', background="#4CAF50", foreground="white", font=('Tahoma', 9, 'bold'), padding=5)
        style.map('Save.TButton', background=[('active', '#66BB6A')])

        style.configure('Reset.TButton', background="#FF5252", foreground="white", font=('Tahoma', 9, 'bold'), padding=5)
        style.map('Reset.TButton', background=[('active', '#FF8A80')])

        self.original_image = None
        self.processed_image = None
        self.tk_image = None

        self.video_capture = None
        self.is_playing = False
        self.after_id = None

        self.create_widgets()

    def create_widgets(self):
        bg_color = "#ECE9D8"
        
        # Left frame for image preview
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.image_canvas = tk.Canvas(self.left_frame, bg="#808080", highlightthickness=0)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.image_canvas.bind("<Configure>", self.on_resize)

        # Right frame with scrollbar for controls
        self.right_frame_container = ttk.Frame(self.root, width=320)
        self.right_frame_container.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_frame_container.pack_propagate(False)

        self.canvas = tk.Canvas(self.right_frame_container, highlightthickness=0, bg=bg_color)
        self.scrollbar = ttk.Scrollbar(self.right_frame_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=300)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Media Controls
        media_frame = ttk.Frame(self.scrollable_frame)
        media_frame.pack(pady=10, fill=tk.X, padx=20)
        
        ttk.Button(media_frame, text="Upload Media", command=self.upload_media, style="Upload.TButton").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.play_btn_var = tk.StringVar(value="Pause")
        self.play_btn = ttk.Button(media_frame, textvariable=self.play_btn_var, command=self.toggle_play, style="Upload.TButton")
        self.play_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Extra Filters Toggles
        toggle_frame = ttk.LabelFrame(self.scrollable_frame, text="Filters")
        toggle_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.toggles = {}
        for toggle in ["Grayscale", "Sepia", "Invert Colors"]:
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(toggle_frame, text=toggle, variable=var, command=self.update_image, bg=bg_color, activebackground=bg_color, font=('Tahoma', 9))
            chk.pack(anchor="w", padx=5, pady=2)
            self.toggles[toggle] = var

        self.sliders = {}
        # Sliders (name, min, max, default)
        self.create_slider("Brightness", -100, 100, 0)
        self.create_slider("Contrast", 0, 300, 100)
        self.create_slider("Blur", 0, 20, 0)
        self.create_slider("Rotation", -180, 180, 0)
        self.create_slider("Zoom", 10, 300, 100)
        self.create_slider("Sharpen", 0, 100, 0)
        self.create_slider("Saturation", -100, 100, 0)
        self.create_slider("Hue", -180, 180, 0)
        self.create_slider("Edge Threshold", 0, 255, 0)
        self.create_slider("Vignette", 0, 100, 0)

        # Bottom Buttons
        ttk.Button(self.scrollable_frame, text="Reset", command=self.reset_image, style="Reset.TButton").pack(pady=10, fill=tk.X, padx=20)
        ttk.Button(self.scrollable_frame, text="Save Frame", command=self.save_media, style="Save.TButton").pack(pady=10, fill=tk.X, padx=20)

    def create_slider(self, name, min_val, max_val, default_val):
        bg_color = "#ECE9D8"
        
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.X, pady=5, padx=10)
        
        lbl = ttk.Label(frame, text=name, font=('Tahoma', 9, 'bold'))
        lbl.pack(anchor="w")
        
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X)
        
        if name in ["Blur", "Edge Threshold"]:
            var = tk.IntVar(value=int(default_val))
        else:
            var = tk.DoubleVar(value=float(default_val))
            
        def on_scale_change(val):
            self.update_image()
            
        def on_entry_change(event=None):
            try:
                v = var.get()
                v = max(min_val, min(v, max_val))
                var.set(v)
                self.update_image()
            except tk.TclError:
                pass

        # Using standard tk.Scale for a chunkier, retro look vs ttk.Scale
        slider = tk.Scale(
            control_frame, 
            from_=min_val, to=max_val, 
            orient=tk.HORIZONTAL, 
            variable=var, 
            command=on_scale_change,
            bg=bg_color,
            troughcolor="#FFFFFF",
            highlightthickness=0,
            showvalue=False,
            relief=tk.SUNKEN,
            bd=2
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        entry = ttk.Entry(control_frame, textvariable=var, width=5, font=('Tahoma', 9))
        entry.pack(side=tk.RIGHT, padx=(5, 0))
        entry.bind("<Return>", on_entry_change)
        entry.bind("<FocusOut>", on_entry_change)

        self.sliders[name] = var

    def upload_media(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Media Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.mp4;*.avi;*.mov;*.mkv"),
            ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),
            ("Video Files", "*.mp4;*.avi;*.mov;*.mkv"),
            ("All files", "*.*")
        ])
        if file_path:
            self.stop_video()
            
            if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                self.video_capture = cv2.VideoCapture(file_path)
                if self.video_capture.isOpened():
                    self.is_playing = True
                    self.play_btn_var.set("Pause")
                    self.reset_sliders()
                    self.update_frame()
                else:
                    messagebox.showerror("Error", "Failed to load video.")
            else:
                img = cv2.imread(file_path)
                if img is not None:
                    self.original_image = img
                    self.reset_sliders()
                    self.process_image()
                else:
                    messagebox.showerror("Error", "Failed to load image.")

    def stop_video(self):
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
            
    def toggle_play(self):
        if self.video_capture:
            self.is_playing = not self.is_playing
            if self.is_playing:
                self.play_btn_var.set("Pause")
                self.update_frame()
            else:
                self.play_btn_var.set("Play")
                
    def update_frame(self):
        if self.video_capture and self.is_playing:
            ret, frame = self.video_capture.read()
            if ret:
                self.original_image = frame
                self.process_image()
                self.after_id = self.root.after(30, self.update_frame) # Approx 30 FPS
            else:
                # Loop video
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.after_id = self.root.after(30, self.update_frame)

    def reset_sliders(self):
        self.sliders["Brightness"].set(0)
        self.sliders["Contrast"].set(100)
        self.sliders["Blur"].set(0)
        self.sliders["Rotation"].set(0)
        self.sliders["Zoom"].set(100)
        self.sliders["Sharpen"].set(0)
        self.sliders["Saturation"].set(0)
        self.sliders["Hue"].set(0)
        self.sliders["Edge Threshold"].set(0)
        self.sliders["Vignette"].set(0)
        
        for toggle in self.toggles.values():
            toggle.set(False)

    def reset_image(self):
        if self.original_image is not None:
            self.reset_sliders()
            self.process_image()

    def update_image(self, event=None):
        if self.original_image is not None and not self.is_playing:
            self.process_image()

    def process_image(self):
        img = self.original_image.copy()

        # Geometry Transformations
        zoom_val = self.sliders["Zoom"].get() / 100.0
        angle = self.sliders["Rotation"].get()
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        if zoom_val != 1.0 or angle != 0:
            M = cv2.getRotationMatrix2D(center, angle, zoom_val)
            img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

        # Filter Toggles
        if self.toggles["Grayscale"].get():
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        if self.toggles["Sepia"].get():
            sepia_kernel = np.array([[0.272, 0.534, 0.131],
                                     [0.349, 0.686, 0.168],
                                     [0.393, 0.769, 0.189]])
            img = cv2.transform(img, sepia_kernel)
            img = np.clip(img, 0, 255).astype(np.uint8)

        if self.toggles["Invert Colors"].get():
            img = cv2.bitwise_not(img)

        # Brightness and Contrast
        brightness = self.sliders["Brightness"].get()
        contrast = self.sliders["Contrast"].get() / 100.0
        if brightness != 0 or contrast != 1.0:
            img = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)

        # Blur
        blur_val = self.sliders["Blur"].get()
        if blur_val > 0:
            k = blur_val * 2 + 1
            img = cv2.GaussianBlur(img, (k, k), 0)

        # Sharpen
        sharpen_val = self.sliders["Sharpen"].get() / 100.0
        if sharpen_val > 0:
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened = cv2.filter2D(img, -1, kernel)
            img = cv2.addWeighted(sharpened, sharpen_val, img, 1.0 - sharpen_val, 0)

        # Hue and Saturation
        hue_val = self.sliders["Hue"].get()
        saturation_val = self.sliders["Saturation"].get()
        if hue_val != 0 or saturation_val != 0:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 0] = (hsv[:, :, 0] + hue_val) % 180
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] + saturation_val, 0, 255)
            hsv = hsv.astype(np.uint8)
            img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
        # Edge Detection Overlay
        edge_val = self.sliders["Edge Threshold"].get()
        if edge_val > 0:
            edges = cv2.Canny(img, int(edge_val), int(edge_val * 2))
            edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            img = cv2.addWeighted(img, 0.5, edges_bgr, 0.5, 0)
            
        # Vignette
        vig_val = self.sliders["Vignette"].get()
        if vig_val > 0:
            std_x = w / (vig_val / 10.0 + 1)
            std_y = h / (vig_val / 10.0 + 1)
            kx = int(w) | 1
            ky = int(h) | 1
            X = cv2.getGaussianKernel(kx, std_x)
            Y = cv2.getGaussianKernel(ky, std_y)
            kernel = Y * X.T
            mask = kernel / kernel.max()
            mask = mask[:h, :w]
            img = (img * mask[..., np.newaxis]).astype(np.uint8)

        self.processed_image = img
        self.display_image()

    def display_image(self):
        if self.processed_image is None:
            return

        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        
        # Resize for display
        lbl_w = self.image_canvas.winfo_width()
        lbl_h = self.image_canvas.winfo_height()
        
        if lbl_w > 10 and lbl_h > 10:
            resample_filter = getattr(Image, 'Resampling', Image).LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
            pil_img.thumbnail((lbl_w, lbl_h), resample_filter)
        
        self.tk_image = ImageTk.PhotoImage(pil_img)
        
        self.image_canvas.delete("all")
        self.image_canvas.create_image(lbl_w // 2, lbl_h // 2, image=self.tk_image, anchor=tk.CENTER)

    def on_resize(self, event):
        self.display_image()

    def save_media(self):
        if self.processed_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                       title="Save Current Frame",
                                                       filetypes=[("PNG files", "*.png"),
                                                                  ("JPEG files", "*.jpg"),
                                                                  ("All files", "*.*")])
            if file_path:
                cv2.imwrite(file_path, self.processed_image)
                messagebox.showinfo("Success", "Frame saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.update()
    root.mainloop()