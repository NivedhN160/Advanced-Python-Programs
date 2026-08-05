import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import cv2
from PIL import Image, ImageTk
import pygame
import threading
import time
import os
import sys
import subprocess

try:
    import whisper
except ImportError:
    print("Error: openai-whisper is not installed.")
    sys.exit(1)

try:
    import imageio_ffmpeg
    import numpy as np
except ImportError:
    print("Error: imageio_ffmpeg or numpy is not installed.")
    sys.exit(1)

class AutoCaptionPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Caption Video Player")
        self.root.geometry("800x650")
        self.root.configure(bg="black")

        pygame.mixer.init()

        # STT Setup
        print("Loading Whisper model (tiny)...")
        self.model = whisper.load_model("tiny")
        print("Whisper model loaded!")

        self.video_path = None
        self.full_audio_array = None
        self.cap = None
        
        self.transcribe_thread = None
        self.is_transcribing = False
        self.current_transcribe_time = 0.0
        self.chunk_duration = 5.0
        self.subtitles = []
        
        self.is_playing = False
        self.audio_offset = 0.0
        self.video_duration = 0.0
        self.video_fps = 30.0

        self.setup_ui()
        self.update_ui()

    def setup_ui(self):
        # Video Frame
        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Subtitle Label
        self.subtitle_label = tk.Label(self.root, text="Open a video to start auto-captioning...", 
                                       font=("Helvetica", 16, "bold"), fg="yellow", bg="black", wraplength=700)
        self.subtitle_label.pack(fill=tk.X, pady=5)

        # Controls Frame
        self.controls_frame = tk.Frame(self.root, bg="#333333")
        self.controls_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Seek Bar
        self.seek_var = tk.DoubleVar()
        self.seek_bar = ttk.Scale(self.controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.seek_var, command=self.seek_video_click)
        self.seek_bar.pack(fill=tk.X, padx=10, pady=5)

        # Buttons Frame
        self.buttons_frame = tk.Frame(self.controls_frame, bg="#333333")
        self.buttons_frame.pack(pady=5)

        self.btn_open = tk.Button(self.buttons_frame, text="Open Video", command=self.open_file, width=15)
        self.btn_open.pack(side=tk.LEFT, padx=10)

        self.btn_play = tk.Button(self.buttons_frame, text="Play", command=self.toggle_play, width=10, state=tk.DISABLED)
        self.btn_play.pack(side=tk.LEFT, padx=10)

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Select a Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.wmv")]
        )
        if not path:
            return

        self.video_path = path
        
        if self.cap:
            self.cap.release()
        pygame.mixer.music.stop()
        self.is_transcribing = False
        if self.transcribe_thread:
            self.transcribe_thread.join()
            
        self.subtitles = []
        self.subtitle_label.config(text="Extracting audio stream (this may take a minute for large movies)...")
        self.root.update()

        try:
            self.cap = cv2.VideoCapture(self.video_path)
            self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
            total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if self.video_fps > 0:
                self.video_duration = total_frames / self.video_fps
            
            self.seek_bar.config(to=self.video_duration)
            
            # Export audio to a temporary file for pygame using ffmpeg directly
            temp_audio_path = "temp_audio_playback.wav"
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            # Extract standard stereo WAV for PyGame
            cmd = [
                ffmpeg_exe, "-y",
                "-i", self.video_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-ac", "2",
                temp_audio_path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            pygame.mixer.music.load(temp_audio_path)
            
            # Load 16kHz mono audio directly into RAM for Whisper
            self.subtitle_label.config(text="Loading audio into memory for STT...")
            self.root.update()
            self.full_audio_array = whisper.load_audio(temp_audio_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video: {e}")
            return

        self.audio_offset = 0.0
        self.cap.set(cv2.CAP_PROP_POS_MSEC, 0)
        pygame.mixer.music.play(start=0.0)
        self.is_playing = True
        self.btn_play.config(text="Pause", state=tk.NORMAL)
        
        self.is_transcribing = True
        self.current_transcribe_time = 0.0
        self.transcribe_thread = threading.Thread(target=self.transcription_worker, daemon=True)
        self.transcribe_thread.start()

    def toggle_play(self):
        if not self.video_path:
            return
            
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.config(text="Play")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.btn_play.config(text="Pause")

    def seek_video_click(self, value):
        if not self.video_path:
            return
        
        seek_time_sec = float(value)
        self.audio_offset = seek_time_sec
        
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_MSEC, seek_time_sec * 1000)
            
        if self.is_playing:
            pygame.mixer.music.play(start=seek_time_sec)
        else:
            pygame.mixer.music.play(start=seek_time_sec)
            pygame.mixer.music.pause()

        self.current_transcribe_time = seek_time_sec

    def transcription_worker(self):
        print("Transcription thread started.")
        sample_rate = 16000
        total_dur = len(self.full_audio_array) / sample_rate if self.full_audio_array is not None else 0
        
        while self.is_transcribing:
            if not self.is_playing:
                time.sleep(0.5)
                continue

            try:
                start_t = self.current_transcribe_time
                end_t = min(start_t + self.chunk_duration, total_dur)
                
                if start_t >= total_dur:
                    time.sleep(1)
                    continue

                # Get actual playback time
                current_time = self.audio_offset + (pygame.mixer.music.get_pos() / 1000.0)
                if pygame.mixer.music.get_pos() == -1:
                    current_time = self.audio_offset
                    
                # Don't transcribe too far ahead (keep ~10s buffer)
                if start_t > current_time + 10.0:
                    time.sleep(0.5)
                    continue

                # Slice the pre-loaded numpy array
                start_idx = int(start_t * sample_rate)
                end_idx = int(end_t * sample_rate)
                chunk_audio = self.full_audio_array[start_idx:end_idx]

                result = self.model.transcribe(chunk_audio, fp16=False)
                text = result.get("text", "").strip()
                
                if text:
                    self.subtitles.append({
                        "start": start_t,
                        "end": end_t,
                        "text": text
                    })
                    print(f"[{start_t:.1f}s - {end_t:.1f}s] {text}")
                
                self.current_transcribe_time = end_t
                
            except Exception as e:
                print("Transcription error:", e)
                time.sleep(1)

    def update_ui(self):
        if self.video_path and self.cap and self.is_playing:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms != -1:
                current_time = self.audio_offset + (pos_ms / 1000.0)
                
                # Sync video to audio
                vid_pos_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
                if current_time * 1000 > vid_pos_ms + 100: # if video is lagging
                    ret, frame = self.cap.read()
                    if ret:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        win_w = self.video_label.winfo_width()
                        win_h = self.video_label.winfo_height()
                        if win_w > 10 and win_h > 10:
                            h, w = frame.shape[:2]
                            scale = min(win_w/w, win_h/h)
                            new_w, new_h = int(w*scale), int(h*scale)
                            frame = cv2.resize(frame, (new_w, new_h))
                            
                        img = Image.fromarray(frame)
                        imgtk = ImageTk.PhotoImage(image=img)
                        self.video_label.imgtk = imgtk
                        self.video_label.configure(image=imgtk)
                
                self.seek_var.set(current_time)
                
                active_text = ""
                for sub in self.subtitles:
                    if sub["start"] <= current_time <= sub["end"]:
                        active_text = sub["text"]
                        break
                
                if active_text:
                    self.subtitle_label.config(text=active_text)
                else:
                    if current_time > self.current_transcribe_time:
                        self.subtitle_label.config(text="[Generating Captions...]")
                    else:
                        self.subtitle_label.config(text="")
        
        self.root.after(30, self.update_ui)

    def on_close(self):
        self.is_transcribing = False
        pygame.mixer.music.stop()
        if self.cap:
            self.cap.release()
        self.root.destroy()
        if os.path.exists("temp_audio_playback.wav"):
            try:
                os.remove("temp_audio_playback.wav")
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoCaptionPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()