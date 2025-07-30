import cv2
from ultralytics import YOLO
from collections import deque, defaultdict
import numpy as np
from llama_cpp import Llama
from tkinter import messagebox
import json
import threading
import tkinter as tk
import time

last_llm_time = 0
llm_cooldown = 10

llm = Llama(
    model_path="models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",  
    n_ctx=512,
    verbose=False
)

last_popup_window = None


def send_to_llm_and_show(data: dict):
    def llm_thread():
        global last_popup_window

        prompt = f"""You are an elderly care expert. Based on the following fall event data, please generate a concise care suggestion or an alert message:Event Data: {json.dumps(data, ensure_ascii=False)}Please respond in English:"""


        res = llm(prompt, max_tokens=600, stop=["</s>"]) #adjust max_token to get detailed outputs
        text_output = res["choices"][0]["text"].strip()


        def show():
            global last_popup_window
            if last_popup_window is not None:
                try:
                    last_popup_window.destroy()
                except:
                    pass

            popup = tk.Toplevel()
            popup.title("LLM Analysis Result")
            popup.geometry("500x300")  
            popup.resizable(True, True)


            frame = tk.Frame(popup)
            frame.pack(fill='both', expand=True)

            scrollbar = tk.Scrollbar(frame)
            scrollbar.pack(side='right', fill='y')

            text_widget = tk.Text(frame, wrap='word', yscrollcommand=scrollbar.set)
            text_widget.insert('1.0', text_output)
            text_widget.config(state='disabled') 
            text_widget.pack(fill='both', expand=True)

            scrollbar.config(command=text_widget.yview)

            tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

            last_popup_window = popup

        try:
            root = tk._default_root
            if root:
                root.after(0, show)
        except:
            pass


    threading.Thread(target=llm_thread, daemon=True).start()

def compute_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) // 2, (y1 + y2) // 2)

def compute_velocity(p1, p2):
    if p1 is None or p2 is None:
        return 0
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def detect_fall_smart(
    video_path,
    fall_model_path='models/best.pt',
    pose_model_path='models/yolov8n-pose.pt',
    save_path='outputs/output.mp4',
    window_size=30,
    vote_threshold=10,
    speed_threshold=20
):
    fall_model = YOLO(fall_model_path)
    pose_model = YOLO(pose_model_path)

    llm_called = False
    cap = cv2.VideoCapture(video_path)
    width, height = int(cap.get(3)), int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))


    fall_history = deque(maxlen=window_size)
    last_centers = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        fall_results = fall_model.predict(source=frame, conf=0.50, iou=0.4)[0]
        current_fall_centers = []
        current_fall_count = 0
        sudden_fall_flag = False

        if fall_results.boxes is not None:
            for i, box in enumerate(fall_results.boxes):
                cls_id = int(box.cls)
                conf = float(box.conf)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                center = compute_center((x1, y1, x2, y2))
                current_fall_centers.append(center)

                if cls_id in [0, 1]:
                    current_fall_count += 1
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"FALL {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


        fall_history.append(current_fall_count > 0)
        persistent_fall = sum(fall_history) >= vote_threshold

        fall_velocity_threshold = 20
        fall_downward_threshold = 15 

        for i in range(min(len(current_fall_centers), len(last_centers))):
            center_now = current_fall_centers[i]
            center_prev = last_centers[i]

            velocity = compute_velocity(center_now, center_prev)
            delta_y = center_now[1] - center_prev[1]  

            if velocity > fall_velocity_threshold and delta_y > fall_downward_threshold:
                sudden_fall_flag = True

        last_centers = current_fall_centers 


        pose_results = pose_model.predict(source=frame, conf=0.25)[0]
        if pose_results.keypoints is not None:
            for kpts in pose_results.keypoints.xy:
                for x, y in kpts:
                    cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 0), -1)
        global last_llm_time
        now = time.time()
        if (persistent_fall or sudden_fall_flag) and now - last_llm_time >= llm_cooldown:
            text = "ALERT: Sustained Fall" if persistent_fall else "ALERT: Sudden Fall"
            cv2.putText(frame, text, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            
            structured_event = {
                "frame": int(cap.get(cv2.CAP_PROP_POS_FRAMES)),
                "fall": True,
                "person_id": 0,  
                "velocity": v if 'v' in locals() else 0,
                "center": current_fall_centers[0] if current_fall_centers else None,
                "bbox": [x1, y1, x2, y2] if 'x1' in locals() else None,
                "fall_type": "sudden" if sudden_fall_flag else "sustained"
            }


            send_to_llm_and_show(structured_event)
            llm_called = True
            last_llm_time = now

        if not persistent_fall and not sudden_fall_flag:
            llm_called = False

        out.write(frame)
        cv2.imshow("Smart Fall Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
