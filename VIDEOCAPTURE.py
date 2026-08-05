import cv2 as cv
from tkinter import Tk, filedialog, messagebox, Menu, Label, Frame, Button
from PIL import Image, ImageTk

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")
        self.root.geometry("800x600")
        
        self.cap = None
        self.is_playing = False
        self.delay = 25
        
        # Create Menu Bar
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Video", command=self.open_file)
        file_menu.add_command(label="Close Video", command=self.close_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Toolbar with buttons
        toolbar = Frame(self.root, bd=1, relief="raised")
        toolbar.pack(side="top", fill="x")
        
        open_btn = Button(toolbar, text="Open", command=self.open_file)
        open_btn.pack(side="left", padx=2, pady=2)
        
        close_btn = Button(toolbar, text="Close", command=self.close_file)
        close_btn.pack(side="left", padx=2, pady=2)
        
        # Video Display Label
        self.video_label = Label(self.root)
        self.video_label.pack(fill="both", expand=True)
        
        # Automatically prompt for video on startup
        self.root.after(100, self.open_file)

    def open_file(self):
        while True:
            # Open a file dialog to select a video
            path = filedialog.askopenfilename(
                title="Select a Video File",
                filetypes=[
                    ("Video Files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                    ("All Files", "*.*")
                ]
            )

            # Check if a file was selected
            if not path:
                if self.cap and self.cap.isOpened():
                    break  # Cancelled while a video is already loaded
                else:
                    messagebox.showerror("Error", "No video file selected. Please select a video file.")
                    continue

            # Check if valid video
            temp_cap = cv.VideoCapture(path)
            if not temp_cap.isOpened():
                messagebox.showerror("Error", "Cannot open the selected video file. Please try another.")
                continue
            
            # Start playing the new video
            self.close_file()
            self.cap = temp_cap
            self.is_playing = True
            
            # Calculate playback delay based on FPS
            fps = self.cap.get(cv.CAP_PROP_FPS)
            if fps > 0:
                self.delay = int(1000 / fps)
            else:
                self.delay = 25
                
            self.update_frame()
            break

    def close_file(self):
        self.is_playing = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.config(image='')
        self.video_label.image = None

    def exit_app(self):
        self.close_file()
        self.root.quit()

    def update_frame(self):
        if self.is_playing and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Resize frame to fit the window while maintaining aspect ratio
                window_width = self.video_label.winfo_width()
                window_height = self.video_label.winfo_height()

                if window_width > 10 and window_height > 10:
                    frame_h, frame_w = frame.shape[:2]
                    
                    scale_w = window_width / frame_w
                    scale_h = window_height / frame_h
                    scale = min(scale_w, scale_h)
                    
                    new_w = int(frame_w * scale)
                    new_h = int(frame_h * scale)
                    
                    if new_w > 0 and new_h > 0:
                        frame = cv.resize(frame, (new_w, new_h), interpolation=cv.INTER_AREA)

                # Convert BGR to RGB for PIL
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                
                # Read next frame
                self.root.after(self.delay, self.update_frame)
            else:
                self.close_file()

if __name__ == "__main__":
    root = Tk()
    app = VideoPlayerApp(root)
    root.mainloop()
