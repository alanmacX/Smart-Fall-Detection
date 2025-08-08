# Smart Fall Detection System

## 📖 Project Overview

This project presents an intelligent fall detection system that integrates computer vision with large language models (LLMs), designed for elderly home safety monitoring. The system utilizes YOLOv8 for fall detection, YOLOv8-Pose for pose visualization, and incorporates TinyLLaMA to provide personalized care advice.

### 🎯 Key Features

- **🔍 Intelligent Detection**: High-precision fall detection powered by a self-trained YOLOv8 model  
- **🎨 Pose Visualization**: Visualizes human skeleton keypoints using YOLOv8-Pose  
- **⚡ Motion Analysis**: Calculates motion speed and applies a sliding window voting mechanism for enhanced robustness  
- **📊 Structured Output**: Includes bounding box positions, motion speeds, fall types, etc.  
- **🤖 Smart Feedback**: Integrates TinyLLaMA to generate personalized caregiving suggestions  
- **💻 Multi-Interface Support**: Available as a desktop GUI and a web application  
- **🔒 Privacy Protection**: Local inference, no data is uploaded to the cloud  

### 🏗️ Project Structure

```
Smart-Fall-Detection-Demo/
├── main.py                 # Core detection logic + LLM analysis
├── gui.py                  # Tkinter-based desktop GUI
├── train.py                # YOLO training script
├── data.yaml               # Dataset configuration
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── 项目情况.txt            # Project details (Chinese)
├── models/                 
│   ├── best.pt            # Self-trained fall detection model
│   ├── yolov8n-pose.pt    # Pose detection model
│   ├── yolov8n.pt         # Base YOLO model
│   └── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf  # LLaMA model
├── outputs/                # Output directory for results
│   └── output_*.mp4       # Processed video files
├── web_fall_detection/     # Full-featured web application
│   ├── app.py             # Flask backend
│   ├── requirements.txt   # Web version dependencies
│   ├── README.md          # Web usage instructions
│   ├── demo.mp4           # Demo video
│   ├── static/            
│   │   ├── css/          
│   │   ├── js/           
│   │   ├── uploads/      
│   │   └── outputs/      
│   ├── templates/         
│   │   ├── index.html    
│   │   ├── result.html   
│   │   └── test_upload.html  
│   └── utils/             
│       ├── detector.py    
│       ├── analyzer.py    
│       ├── demo.py        
│       └── video_converter.py  
└── static/                 
    └── css/               
```

## 🚀 Quick Start

### 1. Environment Setup

#### Clone the repository
```bash
git clone https://github.com/alanmacX/Smart-Fall-Detection-Demo.git
cd Smart-Fall-Detection-Demo
```

#### Install dependencies
```bash
# For desktop version
pip install -r requirements.txt

# For web version
cd web_fall_detection
pip install -r requirements.txt
```

### 2. Download Models

| Model File | Purpose | Download Link | Size |
|------------|---------|---------------|------|
| `best.pt` | Fall detection | *Contact the author* | ~6MB |
| `yolov8n-pose.pt` | Pose estimation | [YOLOv8 Releases](https://github.com/ultralytics/ultralytics/releases) | ~6MB |
| `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` | LLM inference | [HuggingFace](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0) | ~0.6GB |

Place all model files in the `models/` directory.

### 3. Usage

#### 🖥️ Desktop Version (GUI)
```bash
python gui.py
```
1. Click "Import Video" to upload a video  
2. Select the model file paths  
3. Click "Start Detection" to begin  
4. View detection results and LLM analysis in real-time

#### 🌐 Web Version (Recommended)
```bash
cd web_fall_detection
python app.py
```
Then visit `http://localhost:5000`

Web version includes:
- 📱 Responsive design (mobile-friendly)
- 📊 Statistical visualizations
- 🎬 In-browser video playback
- 📈 Performance monitoring
- 🔄 Demo mode (no models required)

## 🛠️ Model Training

### Data Preparation
```bash
dataset/
├── images/
│   ├── train/     
│   └── val/       
└── labels/
    ├── train/     
    └── val/       
```

### Training Config
Edit `data.yaml`:
```yaml
path: ./dataset
train: images/train
val: images/val
nc: 2
names: ["normal", "fall"]
```

### Start Training
```bash
python train.py
# Or via CLI
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=100 imgsz=640
```

## 🎯 Technical Highlights

### Detection Logic
- **Fall Type Recognition**: Detects both sudden and sustained falls  
- **Multi-Verification Mechanism**:  
  - Sliding window voting (30 frames, threshold: 10)  
  - Speed threshold (>20 pixels/frame)  
  - Vertical displacement (>15 pixels drop)  
- **Anti-Interference Design**: Reduces false positives, improves reliability

### Performance Optimizations
- **Frame Skipping**: Configurable skip-frames in web version for speed  
- **GPU Acceleration**: Automatically detects and utilizes GPU  
- **Memory Optimization**: Smart caching to reduce memory usage  
- **Concurrent Processing**: Supports multi-task inference  

### LLM Integration
- **Offline Inference**: Works without internet, ensuring privacy  
- **Structured Input**: Converts detection output into structured LLM input  
- **Personalized Advice**: Custom caregiving suggestions based on fall patterns  
- **Multilingual Support**: Supports both English and Chinese output  

## 📊 System Performance

### Detection Accuracy
- **Precision**: >95% (based on self-trained dataset)  
- **Recall**: >90% (reduces missed falls)  
- **Inference Speed**: 30–60 FPS (GPU) / 10–20 FPS (CPU)

### System Requirements
- **CPU**: Intel i5+ or AMD Ryzen 5+  
- **RAM**: 8GB+ (16GB recommended)  
- **GPU**: Optional, NVIDIA GTX 1060+ recommended  
- **Storage**: 2GB+ (for models & dependencies)

## 🔧 Configuration Options

### Detection Parameters
```python
WINDOW_SIZE = 30
VOTE_THRESHOLD = 10
SPEED_THRESHOLD = 20
CONFIDENCE_THRESHOLD = 0.5
```

### Web Performance Settings
```python
PERFORMANCE_CONFIG = {
    'use_gpu': True,
    'skip_frames': 5,
    'detection_conf': 0.6,
    'iou_threshold': 0.3
}
```

## 🌟 Use Cases

- **🏠 Home Care**: Monitoring elderly living alone  
- **🏥 Medical Facilities**: Patient fall prevention in wards  
- **🏢 Nursing Homes**: Large-scale safety systems  
- **🔬 Academic Research**: For CV and AI studies  
- **💼 Commercial**: Smart security integration  

## 🤝 Contribution Guide

Feel free to submit Issues or Pull Requests!

### Development Setup
```bash
pip install -r requirements.txt
pip install pytest black

pytest tests/

black *.py
```

## 📄 License

MIT License – Free for academic and personal use

## 🙏 Acknowledgments

- **YOLOv8**: Thanks to the Ultralytics team  
- **TinyLLaMA**: Efficient and lightweight LLM  
- **OpenCV**: Powerful computer vision toolkit  
- **Flask**: Minimal yet powerful web framework  

## 📞 Contact

- **Author**: alanmacX  
- **GitHub**: [Smart-Fall-Detection-Demo](https://github.com/alanmacX/Smart-Fall-Detection-Demo)  
- **Email**: *Contact via GitHub*

## 🔄 Changelog

### v2.0.0 (2024)
- ✅ Added web version with online support  
- ✅ Integrated LLaMA for intelligent feedback  
- ✅ Improved performance with GPU acceleration  
- ✅ Expanded documentation and usage guides  

### v1.0.0 (Initial Release)
- ✅ Basic fall detection functionality  
- ✅ Tkinter GUI interface  
- ✅ YOLO model training support  

---

**⭐ If you find this project helpful, please give it a Star!**
