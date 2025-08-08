# Smart Fall Detection System - Project Structure Overview

## 📁 Overall Architecture

This project adopts a modular design, featuring complete desktop and web-based applications with support for both local inference and cloud deployment.

```
Smart-Fall-Detection-Demo/                 # Project root directory
├── 📄 README.md                          # Main project documentation
├── 📄 项目情况.txt                        # Project description (Chinese)
├── 📄 requirements.txt                    # Python dependencies
├── 📄 data.yaml                          # YOLO training data config
├── 📄 main.py                            # Core detection logic
├── 📄 gui.py                             # Desktop GUI interface
├── 📄 train.py                           # Model training script
├── 📁 models/                            # AI model storage
│   ├── 🎯 best.pt                       # Custom trained fall detection model
│   ├── 🎯 yolov8n.pt                    # YOLO base model
│   ├── 🎯 yolov8n-pose.pt               # Pose estimation model
│   └── 🎯 tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf  # LLaMA language model
├── 📁 outputs/                           # Detection output
│   └── 🎬 output_*.mp4                   # Processed video files
├── 📁 static/                            # Static resources
│   └── 📁 css/                          # Style files
├── 📁 __pycache__/                       # Python cache
└── 📁 web_fall_detection/                # Full web application
    ├── 📄 README.md                      # Web version README
    ├── 📄 requirements.txt               # Web-specific dependencies
    ├── 📄 app.py                         # Flask main app
    ├── 🎬 demo.mp4                       # Demo video
    ├── 📁 static/                        # Static resources for web
    │   ├── 📁 css/                      # Stylesheets
    │   │   └── 🎨 style.css             # Main stylesheet
    │   ├── 📁 js/                       # JavaScript files
    │   │   └── 📜 main.js               # Main script
    │   ├── 📁 uploads/                  # User upload folder
    │   └── 📁 outputs/                  # Web output folder
    ├── 📁 templates/                     # HTML templates
    │   ├── 🌐 index.html               # Homepage
    │   ├── 🌐 result.html              # Result display page
    │   └── 🌐 test_upload.html         # Upload testing page
    ├── 📁 utils/                        # Utility modules
    │   ├── 📄 detector.py               # Detection core class
    │   ├── 📄 detector_backup.py        # Backup version
    │   ├── 📄 analyzer.py               # Result analyzer
    │   ├── 📄 demo.py                   # Demo mode
    │   ├── 📄 video_converter.py        # Video converter
    │   └── 📁 __pycache__/              # Python cache
    └── 📁 __pycache__/                   # Python cache
```

## 🧩 Core Module Functions

### 1. Desktop Components

#### 📄 `main.py` - Core Detection Engine
- **Function**: Implements fall detection logic
- **Includes**: YOLO detection, pose analysis, LLM integration
- **Highlights**:
  - Sliding window voting mechanism
  - Speed and displacement analysis
  - Real-time LLM feedback
  - Multi-threading

#### 📄 `gui.py` - Desktop GUI Interface
- **Function**: Tkinter-based GUI
- **Features**:
  - File selection and preview
  - Progress display
  - LLM analysis popup
  - User-friendly workflow

#### 📄 `train.py` - Model Training Script
- **Function**: YOLOv8 training
- **Supports**:
  - Custom dataset training
  - Resume training
  - Hyperparameter tuning
  - Training visualization

### 2. Web Components

#### 📄 `app.py` - Flask Web App
- **Function**: Main web entry point
- **Features**:
  - RESTful API design
  - Multi-task concurrency
  - Performance monitoring
  - Error handling and recovery
  - Demo mode support

#### 📁 `utils/` - Utility Modules

##### 📄 `detector.py` - Detection Core Class
- **Function**: OOP-based logic abstraction
- **Optimizations**:
  - GPU support
  - Frame skipping
  - Memory management
  - Thread-safe

##### 📄 `analyzer.py` - Result Analyzer
- **Function**: Statistical analysis and visualization
- **Output**:
  - Fall statistics
  - Time distribution
  - Confidence analysis
  - Risk assessment

##### 📄 `demo.py` - Demo Mode
- **Function**: Run without actual models
- **Highlights**:
  - Simulated output
  - Preserves UI structure
  - Low entry barrier

##### 📄 `video_converter.py` - Video Processing
- **Function**: Format conversion and optimization
- **Supports**:
  - Multiple formats
  - Compression and quality control
  - Web compatibility

### 3. AI Model Components

#### 🎯 `best.pt` - Fall Detection Model
- **Type**: Custom YOLOv8 model
- **Function**: Classify normal vs fall states
- **Classes**: 0-normal, 1-fall
- **Optimized for**: Elderly movement

#### 🎯 `yolov8n-pose.pt` - Pose Estimation Model
- **Type**: YOLOv8 pose model
- **Function**: Detect body keypoints
- **Purpose**: Visualization enhancement

#### 🎯 `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` - Language Model
- **Type**: Quantized LLaMA model
- **Function**: Generate care advice and analysis
- **Features**: Local inference, privacy-friendly

## 🔄 Data Flow

### Desktop Flow
```
User selects video → GUI interface → main.py detection → LLM feedback popup
```

### Web Flow
```
User uploads video → Flask receives → detector.py processes → analyzer.py analyzes → Display results
```

## 💾 File Structure

### Input Files
- **Video**: Supports mp4, avi, mov
- **Models**: .pt and .gguf formats
- **Config**: YAML

### Output Files
- **Processed Videos**: Annotated mp4
- **Reports**: JSON detection results
- **Logs**: System logs

## 🔧 Config File Notes

### `data.yaml` - YOLO Data Config
```yaml
path: .                    # Dataset root path
train: images/train        # Training images
val: images/val            # Validation images
nc: 2                     # Number of classes
names: ["normal", "fall"] # Class names
```

### `requirements.txt` - Dependencies
- **Layered**: Core + optional
- **Versioned**: Minimum versions enforced
- **Cross-platform**: Windows/Linux/Mac

## 📊 Performance Optimizations

### 1. Detection
- **Frame skipping**: Adjustable intervals
- **GPU acceleration**: Auto GPU detection
- **Batch processing**: Efficiency

### 2. Memory
- **Streaming**: Avoid full memory load
- **Cache cleaning**: Smart cleanup
- **GC**: Manual garbage collection

### 3. Concurrency
- **Multithreading**: Non-blocking GUI
- **Task queue**: Web task handling
- **Progress bar**: Real-time status

## 🔒 Privacy & Security

### Privacy
- **Local processing**: No cloud upload
- **Local inference**: All AI local
- **Auto cleanup**: Temporary file removal

### Security
- **File checks**: Safe formats only
- **Path security**: No traversal
- **Resource limits**: Prevent DoS

## 🚀 Deployment Advice

### Dev Environment
- Python 3.8+
- 8GB+ RAM
- Optional GPU

### Production
- **Web**: Gunicorn + Nginx
- **Container**: Docker supported
- **Scaling**: Multi-instance

### Extensibility
- **API**: 3rd-party integration
- **Plugin**: New feature support
- **Configurable**: Easy tuning

This modular, extensible design supports both research and production use cases.
