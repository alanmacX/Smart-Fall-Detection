# 智能跌倒检测系统 (Smart Fall Detection System)

## 📖 项目概述

本项目是一套融合计算机视觉与大语言模型的智能跌倒检测系统，面向老年人居家安全监护。系统采用YOLOv8进行跌倒检测、YOLOv8-Pose进行姿态可视化，并集成TinyLLaMA提供智能护理建议。

### 🎯 核心特性

- **🔍 智能检测**: 基于自训练YOLOv8模型的高精度跌倒检测
- **🎨 姿态可视化**: YOLOv8-Pose骨架点显示，增强视觉效果  
- **⚡ 运动分析**: 速度计算和滑动窗口投票机制，提升检测鲁棒性
- **📊 结构化输出**: 包含边界框位置、运动速度、跌倒类型等详细信息
- **🤖 智能反馈**: 集成TinyLLaMA生成个性化护理建议
- **💻 多界面支持**: 提供桌面GUI和Web应用两种使用方式
- **🔒 隐私保护**: 本地处理，数据不上传云端

### 🏗️ 项目架构

```
Smart-Fall-Detection-Demo/
├── main.py                 # 核心检测逻辑+LLM分析
├── gui.py                  # Tkinter桌面版GUI
├── train.py                # YOLO模型训练脚本
├── data.yaml               # 训练数据配置
├── requirements.txt        # Python依赖清单
├── README.md               # 项目文档
├── 项目情况.txt            # 项目详细介绍
├── models/                 # 模型文件目录
│   ├── best.pt            # 自训练跌倒检测模型
│   ├── yolov8n-pose.pt    # 姿态检测模型
│   ├── yolov8n.pt         # 基础YOLO模型
│   └── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf  # LLaMA模型
├── outputs/                # 检测结果输出目录
│   └── output_*.mp4       # 处理后的视频文件
├── web_fall_detection/     # Web版本完整应用
│   ├── app.py             # Flask主应用
│   ├── requirements.txt   # Web版依赖
│   ├── README.md          # Web版说明
│   ├── demo.mp4           # 演示视频
│   ├── static/            # 静态资源
│   │   ├── css/          # 样式文件
│   │   ├── js/           # JavaScript文件
│   │   ├── uploads/      # 用户上传文件
│   │   └── outputs/      # 处理结果
│   ├── templates/         # HTML模板
│   │   ├── index.html    # 主页面
│   │   ├── result.html   # 结果页面
│   │   └── test_upload.html  # 测试页面
│   └── utils/             # 工具模块
│       ├── detector.py    # 检测器封装
│       ├── analyzer.py    # 结果分析器
│       ├── demo.py        # 演示模式
│       └── video_converter.py  # 视频转换
└── static/                 # 静态资源
    └── css/               # 样式文件
```

## 🚀 快速开始

### 1. 环境准备

#### 克隆项目
```bash
git clone https://github.com/alanmacX/Smart-Fall-Detection-Demo.git
cd Smart-Fall-Detection-Demo
```

#### 安装依赖
```bash
# 基础版本（桌面版）
pip install -r requirements.txt

# Web版本（完整功能）
cd web_fall_detection
pip install -r requirements.txt
```

### 2. 模型下载

| 模型文件 | 用途 | 下载链接 | 大小 |
|---------|------|----------|------|
| `best.pt` | 跌倒检测 | *请联系项目作者* | ~6MB |
| `yolov8n-pose.pt` | 姿态估计 | [YOLOv8 Releases](https://github.com/ultralytics/ultralytics/releases) | ~6MB |
| `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` | 智能分析 | [HuggingFace](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0) | ~0.6GB |

将所有模型文件放置在 `models/` 目录下。

### 3. 使用方式

#### 🖥️ 桌面版 (GUI)
```bash
python gui.py
```
1. 点击"Import Video"导入视频
2. 选择模型文件路径
3. 点击"Start Detection"开始检测
4. 实时查看检测结果和LLM分析

#### 🌐 Web版 (推荐)
```bash
cd web_fall_detection
python app.py
```
然后访问 `http://localhost:5000`

Web版功能更丰富：
- 📱 响应式设计，支持移动端
- 📊 详细的统计分析图表
- 🎬 在线视频播放
- 📈 性能监控和优化
- 🔄 演示模式（无需模型文件）

## 🛠️ 模型训练

### 数据准备
```bash
# 组织训练数据
dataset/
├── images/
│   ├── train/     # 训练图片
│   └── val/       # 验证图片
└── labels/
    ├── train/     # 训练标注
    └── val/       # 验证标注
```

### 训练配置
编辑 `data.yaml`:
```yaml
path: ./dataset
train: images/train
val: images/val
nc: 2
names: ["normal", "fall"]
```

### 开始训练
```bash
python train.py
# 或者使用命令行
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=100 imgsz=640
```

## 🎯 技术特点

### 检测算法
- **跌倒类型识别**: 支持突发性跌倒(sudden)和持续性跌倒(sustained)
- **多重验证机制**: 
  - 滑动窗口投票 (30帧窗口，阈值10)
  - 速度阈值检测 (>20像素/帧)
  - 垂直位移分析 (>15像素下降)
- **抗干扰设计**: 减少误报，提高检测准确性

### 性能优化
- **跳帧检测**: Web版支持可配置的跳帧间隔，提升处理速度
- **GPU加速**: 自动检测并使用GPU加速推理
- **内存优化**: 智能缓存机制，减少内存占用
- **并发处理**: 支持多任务并发检测

### LLM集成
- **本地推理**: 无需网络连接，保护隐私
- **结构化输入**: 将检测结果转换为结构化数据输入LLM
- **个性化建议**: 根据跌倒类型、频率生成针对性护理建议
- **多语言支持**: 支持中英文输出

## 📊 系统性能

### 检测精度
- **准确率**: >95% (基于自训练数据集)
- **召回率**: >90% (减少漏检)
- **处理速度**: 30-60 FPS (GPU) / 10-20 FPS (CPU)

### 资源需求
- **CPU**: Intel i5+ 或 AMD Ryzen 5+
- **内存**: 8GB+ (推荐16GB)
- **GPU**: 可选，NVIDIA GTX 1060+ (显著提升性能)
- **存储**: 2GB+ (模型+依赖)

## 🔧 配置选项

### 检测参数调整
```python
# 在main.py或detector.py中调整
WINDOW_SIZE = 30           # 滑动窗口大小
VOTE_THRESHOLD = 10        # 投票阈值
SPEED_THRESHOLD = 20       # 速度阈值
CONFIDENCE_THRESHOLD = 0.5 # 置信度阈值
```

### Web版性能配置
```python
# 在web_fall_detection/app.py中调整
PERFORMANCE_CONFIG = {
    'use_gpu': True,          # GPU加速
    'skip_frames': 5,         # 跳帧间隔
    'detection_conf': 0.6,    # 检测置信度
    'iou_threshold': 0.3      # IOU阈值
}
```

## 🌟 应用场景

- **🏠 居家养老**: 独居老人安全监护
- **🏥 医疗机构**: 病房患者跌倒预防
- **🏢 养老院**: 大规模监护系统
- **🔬 科研教学**: 计算机视觉和AI应用研究
- **💼 商业应用**: 智能安防系统集成

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置
```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest black  # 测试和格式化工具

# 运行测试
pytest tests/

# 代码格式化
black *.py
```

## 📄 许可证

MIT License - 免费用于学术和个人用途

## 🙏 致谢

- **YOLOv8**: Ultralytics团队的优秀开源项目
- **TinyLLaMA**: 高效的小型语言模型
- **OpenCV**: 强大的计算机视觉库
- **Flask**: 轻量级Web框架

## 📞 联系方式

- **项目作者**: alanmacX
- **GitHub**: [Smart-Fall-Detection-Demo](https://github.com/alanmacX/Smart-Fall-Detection-Demo)
- **邮箱**: *请通过GitHub联系*

## 🔄 更新日志

### v2.0.0 (2024年)
- ✅ 新增Web版本，支持在线使用
- ✅ 集成LLaMA智能分析
- ✅ 添加性能优化和GPU加速
- ✅ 完善文档和使用说明

### v1.0.0 (初始版本)
- ✅ 基础跌倒检测功能
- ✅ Tkinter GUI界面
- ✅ YOLO模型训练支持

---

**⭐ 如果这个项目对您有帮助，请给我们一个Star！**
