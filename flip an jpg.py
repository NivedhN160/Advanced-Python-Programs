import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import base64

class ImageFlipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Flipper GUI")
        self.root.geometry("800x600")
        
        self.original_image = None
        self.display_image = None
        self.photo = None
        
        # UI Setup
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        self.btn_open = tk.Button(self.control_frame, text="Open Image", command=self.open_image)
        self.btn_open.pack(side=tk.LEFT, padx=5)
        
        self.btn_h_flip = tk.Button(self.control_frame, text="-", command=self.flip_horizontal, state=tk.DISABLED)
        self.btn_h_flip.pack(side=tk.LEFT, padx=5)
        
        self.btn_v_flip = tk.Button(self.control_frame, text="|", command=self.flip_vertical, state=tk.DISABLED)
        self.btn_v_flip.pack(side=tk.LEFT, padx=5)
        
        self.btn_b_flip = tk.Button(self.control_frame, text="-+|", command=self.flip_both, state=tk.DISABLED)
        self.btn_b_flip.pack(side=tk.LEFT, padx=5)
        
        self.btn_restore = tk.Button(self.control_frame, text="Restore Original", command=self.restore_image, state=tk.DISABLED)
        self.btn_restore.pack(side=tk.LEFT, padx=5)

        self.btn_save = tk.Button(self.control_frame, text="Save Image", command=self.save_image, state=tk.DISABLED)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        self.canvas = tk.Canvas(root, bg="gray")
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize)
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is None:
                messagebox.showerror("Error", "Unable to read the image.")
                return
            
            self.display_image = self.original_image.copy()
            self.update_display()
            self.enable_buttons()
            
    def enable_buttons(self):
        self.btn_h_flip.config(state=tk.NORMAL)
        self.btn_v_flip.config(state=tk.NORMAL)
        self.btn_b_flip.config(state=tk.NORMAL)
        self.btn_restore.config(state=tk.NORMAL)
        self.btn_save.config(state=tk.NORMAL)
        
    def on_resize(self, event):
        if self.display_image is not None:
            self.update_display()
        
    def update_display(self):
        if self.display_image is None:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10:
            return
            
        # Calculate aspect ratio preserving dimensions
        img_h, img_w = self.display_image.shape[:2]
        
        scale_w = canvas_width / img_w
        scale_h = canvas_height / img_h
        scale = min(scale_w, scale_h)
        
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        if new_w > 0 and new_h > 0:
            resized_img = cv2.resize(self.display_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            success, buffer = cv2.imencode('.png', resized_img)
            if success:
                b64_data = base64.b64encode(buffer).decode('utf-8')
                self.photo = tk.PhotoImage(data=b64_data)
                self.canvas.delete("all")
                self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo, anchor=tk.CENTER)
            
    def flip_horizontal(self):
        if self.original_image is not None:
            self.display_image = cv2.flip(self.original_image, 1)
            self.update_display()
            
    def flip_vertical(self):
        if self.original_image is not None:
            self.display_image = cv2.flip(self.original_image, 0)
            self.update_display()
            
    def flip_both(self):
        if self.original_image is not None:
            self.display_image = cv2.flip(self.original_image, -1)
            self.update_display()
            
    def restore_image(self):
        if self.original_image is not None:
            self.display_image = self.original_image.copy()
            self.update_display()

    def save_image(self):
        if self.display_image is not None:
            file_path = filedialog.asksaveasfilename(
                title="Save Image",
                defaultextension=".jpg",
                filetypes=[
                    ("JPEG", "*.jpg"),
                    ("PNG", "*.png"),
                    ("All Files", "*.*")
                ]
            )
            if file_path:
                cv2.imwrite(file_path, self.display_image)
                messagebox.showinfo("Success", "Image saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageFlipperApp(root)
    root.mainloop()
