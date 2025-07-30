
# Smart Fall Detection System Demo (YOLO + Pose + LLM + GUI)

This project implements an intelligent fall detection system combining YOLOv8 for object detection, YOLOv8-Pose for skeleton visualization, and TinyLLaMA for local natural language feedback. It includes a lightweight GUI for user-friendly interaction.

---

##  Features

- **Fall detection** using custom-trained YOLOv8
- **Pose overlay** with YOLOv8-Pose (non-intrusive, only for visualization)
- **Speed calculation** and **sliding window voting** for robust fall judgment
- **Structured fall data output**, including:
  - Bounding box location
  - Movement speed
  - Fall type (sustained / sudden)
- **LLM feedback** with prompt engineering: sends structured data to TinyLLaMA to generate care advice
- **Popup feedback** displayed in GUI
- **User-friendly interface** to load videos and run detection

---

##  Project Structure

```
fall-detection/
├── main.py             # Main fall detection + pose + logic + LLM output
├── gui.py              # Tkinter GUI, handles file input and video display
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── .gitignore          # Ignoring large files like .pt/.mp4
└── models/             # Store model weights here (not pushed to Git)
```

---

##  Installation

### 1. Clone the repo:

```bash
git clone https://github.com/your-username/fall-detection.git
cd fall-detection
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

##  Download Required Models (Manual)

| File               | Purpose                 | Link |
|--------------------|--------------------------|------|
| `best.pt`          | Trained fall detector    | *(Upload your link here)* |
| `yolov8x-pose.pt`  | Pose estimation model    | [YOLOv8 Releases](https://github.com/ultralytics/ultralytics/releases) |
| `tinyllama.gguf`   | Local LLM weights        | [TinyLLaMA on HuggingFace](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0) |

 Place them in the `models/` directory:

```
fall-detection/
└── models/
    ├── best.pt
    ├── yolov8x-pose.pt
    └── tinyllama.gguf
```

---

##  Usage

### Start the GUI:

```bash
python gui.py
```

Then in the GUI:

1. Click “Import Video"
2. Click “Start Detection"
3. See detection + pose + fall feedback
4. Pop-up windows give real-time care suggestions based on LLM interpretation

---

##  LLM Setup (TinyLLaMA)

1. Install llama-cpp-python:

```bash
pip install llama-cpp-python
```

2. Make sure `tinyllama.gguf` is in `models/`
3. `llm_utils.py` uses structured fall data to send prompts and parse replies

Prompt format example:

```text
A person has fallen near the center of the video frame at a speed of 2.3.
Give a one-sentence first-aid suggestion.
```

---

##  Example Screenshot

> You can insert your own demo frame here.

```
[screenshot coming soon]
```

---

## ️ Notes

- All model files (`.pt`, `.gguf`, `.mp4`) are ignored in `.gitignore`
- This system is designed to run fully offline
- Ideal for eldercare AI system prototyping

---

##  License

MIT License. Free for academic and personal use.


---

##  Model Training

To train your own fall detection model using YOLOv8, follow these steps:

### 1. Prepare your dataset

Organize your data in YOLO format:

```
fall-dataset/
├── images/
   ├── train/
   └── val/
├── labels/
   ├── train/
   └── val/
└── data.yaml
```

The `data.yaml` should contain:

```yaml
train: path/to/images/train
val: path/to/images/val
nc: 2
names: ["normal", "fall"]
```

> Ensure that 0 = normal, 1 = fall.

---

### 2. Run training command:

```bash
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=50 imgsz=640
```

You can also resume or use your own pretrained weight:

```bash
yolo task=detect mode=train model=models/best.pt data=data.yaml epochs=50 imgsz=640 resume=True
```

---

### 3. After training

- Best weights will be saved to `runs/detect/train/weights/best.pt`
- Replace the detection model in `main.py` with your new path if needed.
