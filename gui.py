import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import main

class FallDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fall Detection GUI")
        self.root.geometry("620x260")
        self.root.resizable(False, False)

        self.video_path = tk.StringVar()
        self.model_path = tk.StringVar()
        self.pose_path = tk.StringVar(value="yolov8x-pose.pt")


        ttk.Label(root, text="Video File:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(root, textvariable=self.video_path, width=50).grid(row=0, column=1)
        ttk.Button(root, text="Browse", command=self.browse_video).grid(row=0, column=2)

        ttk.Label(root, text="Fall Model:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(root, textvariable=self.model_path, width=50).grid(row=1, column=1)
        ttk.Button(root, text="Browse", command=self.browse_model).grid(row=1, column=2)

        ttk.Label(root, text="Pose Model:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(root, textvariable=self.pose_path, width=50).grid(row=2, column=1)
        ttk.Button(root, text="Browse", command=self.browse_pose).grid(row=2, column=2)

        ttk.Button(root, text="Run Fall Detection", command=self.run_detection).grid(row=3, column=1, pady=15)

        self.status_label = ttk.Label(root, text="Ready", foreground="green")
        self.status_label.grid(row=4, column=0, columnspan=3)

    def browse_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if path:
            self.video_path.set(path)

    def browse_model(self):
        path = filedialog.askopenfilename(filetypes=[("YOLO Model", "*.pt")])
        if path:
            self.model_path.set(path)

    def browse_pose(self):
        path = filedialog.askopenfilename(filetypes=[("Pose Model", "*.pt")])
        if path:
            self.pose_path.set(path)

    def run_detection(self):
        video = self.video_path.get()
        model = self.model_path.get()
        pose = self.pose_path.get()

        if not video or not model:
            messagebox.showerror("Missing Input", "Please select both video and fall model.")
            return

        self.status_label.config(text="Running detection...", foreground="orange")
        threading.Thread(target=self._detect_thread, args=(video, model, pose)).start()

    def _detect_thread(self, video, model, pose):
        try:
            main.detect_fall_smart(video, model, pose_model_path=pose)
            self.status_label.config(text="Detection Complete", foreground="green")
            messagebox.showinfo("Done", "Detection finished. Saved as output.mp4.")
        except Exception as e:
            self.status_label.config(text="Error", foreground="red")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FallDetectionApp(root)
    root.mainloop()