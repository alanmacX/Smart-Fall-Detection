# 智能跌倒检测Web系统

## 🎯 项目简介

智能跌倒检测Web系统是基于深度学习的老年人安全监护解决方案，采用YOLOv8进行跌倒检测、TinyLLaMA提供智能分析，通过Web界面提供便捷的用户体验。

## 🌟 核心特性

### 🔍 智能检测能力
- **双模式检测**: 支持突发性跌倒和持续性跌倒识别
- **高精度算法**: 基于自训练YOLOv8模型，准确率>95%
- **姿态可视化**: YOLOv8-Pose关键点显示，增强视觉效果
- **速度优化**: 支持跳帧检测，处理速度提升3-5倍

### � AI智能分析
- **本地LLaMA**: 集成TinyLLaMA-1.1B模型，无需联网
- **个性化建议**: 根据跌倒类型生成针对性护理建议
- **风险评估**: 自动评估低/中/高三级风险等级
- **多语言支持**: 中英文智能分析输出

### 📊 可视化分析
- **实时图表**: 动态显示检测置信度和事件分布
- **交互式界面**: 响应式设计，支持移动端访问
- **详细报告**: 包含时间线、统计数据、性能指标
- **结果导出**: 支持视频和分析报告下载

### 🔒 隐私安全
- **本地处理**: 所有AI推理在本地完成
- **数据不上传**: 原始视频不离开本地设备
- **自动清理**: 处理完成后自动清理临时文件
- **无存储**: 不保存用户个人数据

## 🏗️ 技术架构

```
前端层 (Frontend)
├── HTML5 + Bootstrap 4       # 响应式界面
├── JavaScript + jQuery       # 交互逻辑
├── Chart.js                  # 数据可视化
└── WebRTC (可选)             # 实时视频流

后端层 (Backend)
├── Flask 2.3+                # Web框架
├── Werkzeug                  # WSGI工具
├── 异步任务队列              # 多任务处理
└── RESTful API               # 接口设计

AI引擎层 (AI Engine)
├── YOLOv8 检测器             # 跌倒检测
├── YOLOv8-Pose               # 姿态估计
├── TinyLLaMA                 # 智能分析
└── 结果分析器                # 统计分析

系统层 (System)
├── OpenCV                    # 视频处理
├── NumPy/SciPy              # 数值计算
├── 并发控制                  # 资源管理
└── 错误恢复                  # 容错机制
```

## 🚀 安装部署

### 1. 环境准备

#### 系统要求
- **操作系统**: Windows 10+ / Ubuntu 18.04+ / macOS 10.15+
- **Python版本**: 3.8+
- **内存要求**: 8GB+ (推荐16GB)
- **存储空间**: 5GB+ (模型文件+依赖)
- **GPU**: 可选，NVIDIA GTX 1060+ (显著提升性能)

#### 克隆项目
```bash
git clone https://github.com/alanmacX/Smart-Fall-Detection-Demo.git
cd Smart-Fall-Detection-Demo/web_fall_detection
```

### 2. 安装依赖

#### 基础安装
```bash
# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### GPU加速 (可选)
```bash
# 如果有NVIDIA GPU，安装CUDA版本的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. 模型配置

#### 下载模型文件
将以下模型文件放置在 `../models/` 目录：

| 模型文件 | 用途 | 大小 | 获取方式 |
|---------|------|------|----------|
| `best.pt` | 跌倒检测 | ~6MB | 联系项目作者 |
| `yolov8n-pose.pt` | 姿态检测 | ~6MB | [YOLOv8官网](https://github.com/ultralytics/ultralytics) |
| `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` | 智能分析 | ~0.6GB | [HuggingFace](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0) |

#### 模型目录结构
```
../models/
├── best.pt                                    # 自训练跌倒检测模型
├── yolov8n-pose.pt                           # 姿态检测模型
└── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf     # LLaMA语言模型
```

### 4. 启动服务

#### 开发模式
```bash
python app.py
```
访问: `http://localhost:5000`

#### 生产模式
```bash
# 使用Gunicorn (Linux/Mac)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 使用Waitress (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

## 💻 使用指南

### 基本操作流程

1. **上传视频**
   - 支持格式: MP4, AVI, MOV
   - 最大文件: 500MB
   - 建议分辨率: 640x480以上

2. **配置参数**
   - 检测置信度: 0.1-0.9 (默认0.6)
   - 跳帧间隔: 1-10帧 (默认5)
   - GPU加速: 自动检测

3. **开始检测**
   - 实时进度显示
   - 处理状态监控
   - 错误自动恢复

4. **查看结果**
   - 在线视频播放
   - 详细统计分析
   - LLM智能建议
   - 结果下载

### 界面功能说明

#### 主页面 (`/`)
- **文件上传区**: 拖拽或点击上传视频
- **参数配置**: 调整检测参数
- **演示模式**: 无模型文件时的功能演示

#### 结果页面 (`/result/<task_id>`)
- **视频播放器**: 播放处理后的标注视频
- **统计图表**: 检测事件时间线和置信度分布
- **智能分析**: LLaMA生成的护理建议
- **性能监控**: 处理速度和资源使用情况

#### API接口
- `POST /upload`: 上传视频文件
- `GET /status/<task_id>`: 查询处理状态
- `GET /result/<task_id>`: 获取检测结果
- `GET /download/<task_id>`: 下载结果文件

## ⚙️ 配置选项

### 性能配置
```python
# 在app.py中调整
PERFORMANCE_CONFIG = {
    'use_gpu': True,           # 启用GPU加速
    'skip_frames': 5,          # 跳帧间隔（1-10）
    'detection_conf': 0.6,     # 检测置信度阈值
    'iou_threshold': 0.3,      # IOU阈值
    'max_workers': 4           # 最大并发任务数
}
```

### 文件配置
```python
# 文件上传限制
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

# 目录配置
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
```

### 检测参数
```python
# 检测算法参数
DETECTION_CONFIG = {
    'window_size': 30,         # 滑动窗口大小
    'vote_threshold': 10,      # 投票阈值
    'speed_threshold': 20,     # 速度阈值
    'confidence_threshold': 0.5 # 置信度阈值
}
```

## 📊 功能特色

### 1. 演示模式
当模型文件不可用时，系统自动切换到演示模式：
- 生成模拟检测结果
- 保持完整界面功能
- 便于功能展示和测试

### 2. 性能优化
- **跳帧检测**: 可配置的帧间隔，平衡精度和速度
- **GPU加速**: 自动检测并使用GPU，处理速度提升3-10倍
- **内存管理**: 流式处理，避免内存溢出
- **并发控制**: 支持多任务同时处理

### 3. 错误恢复
- **自动重试**: 检测失败时自动重试
- **状态保持**: 进度持久化，防止丢失
- **错误反馈**: 详细的错误信息和解决建议

### 4. 数据可视化
- **实时图表**: 使用Chart.js绘制动态图表
- **响应式设计**: 支持桌面和移动端
- **交互体验**: 可点击、缩放的数据面板

## 🔧 开发指南

### 项目结构
```
web_fall_detection/
├── app.py                 # Flask主应用
├── requirements.txt       # 依赖文件
├── README.md             # 说明文档
├── demo.mp4              # 演示视频
├── static/               # 静态资源
│   ├── css/style.css    # 样式文件
│   ├── js/main.js       # 前端脚本
│   ├── uploads/         # 上传文件
│   └── outputs/         # 输出文件
├── templates/            # HTML模板
│   ├── index.html       # 主页
│   ├── result.html      # 结果页
│   └── test_upload.html # 测试页
└── utils/               # 工具模块
    ├── detector.py      # 检测器
    ├── analyzer.py      # 分析器
    ├── demo.py          # 演示模式
    └── video_converter.py # 视频转换
```

### 代码规范
- **PEP 8**: Python代码风格
- **类型注解**: 使用type hints
- **文档字符串**: 详细的函数说明
- **错误处理**: 完善的异常捕获

### 测试
```bash
# 运行测试页面
python app.py
# 访问 http://localhost:5000/test 进行功能测试

# 单元测试 (如果配置)
pytest tests/
```

## � 故障排除

### 常见问题

1. **模型加载失败**
   ```
   解决方案：
   - 检查模型文件路径
   - 确认文件完整性
   - 查看系统内存是否充足
   ```

2. **GPU加速不可用**
   ```
   解决方案：
   - 安装CUDA驱动
   - 安装PyTorch GPU版本
   - 检查GPU内存是否充足
   ```

3. **视频处理失败**
   ```
   解决方案：
   - 确认视频格式支持
   - 检查文件是否损坏
   - 验证OpenCV安装
   ```

4. **内存不足**
   ```
   解决方案：
   - 调整跳帧参数
   - 降低视频分辨率
   - 增加系统内存
   ```

### 日志查看
系统会在控制台输出详细的处理日志：
```bash
🔄 正在加载模型...
✅ YOLO模型加载完成 (设备: cuda)
⚡ 跳帧设置: 每5帧检测1次
📁 上传目录: /path/to/uploads
📁 输出目录: /path/to/outputs
```

## 🔮 未来规划

### 短期目标
- [ ] 增加实时摄像头检测
- [ ] 支持多人同时检测
- [ ] 添加更多视频格式支持
- [ ] 优化移动端体验

### 长期目标
- [ ] 微服务架构重构
- [ ] 云端部署支持
- [ ] 多语言界面
- [ ] 行为模式分析

## 📞 技术支持

如遇到问题，请通过以下方式获取帮助：

1. **查看文档**: 阅读完整的README和项目文档
2. **GitHub Issues**: 在项目仓库提交问题
3. **演示模式**: 使用演示模式验证功能
4. **日志分析**: 查看控制台输出的详细日志

## 📄 开源许可

本项目采用MIT许可证，免费用于学术和个人用途。
- 至少4GB RAM
- 支持CUDA的GPU（可选，用于加速）

### 安装步骤

1. **克隆项目**
```bash
cd Smart-Fall-Detection-Demo/web_fall_detection
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **模型文件准备**
确保以下模型文件存在：
```
../models/
├── best.pt                    # YOLO跌倒检测模型
├── yolov8n-pose.pt           # YOLO姿态检测模型
└── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf  # LLaMA模型
```

4. **启动系统**
```bash
python app.py
```

5. **访问系统**
打开浏览器访问: `http://localhost:5000`

## 📖 使用指南

### 1. 视频上传
- 支持格式：MP4、AVI、MOV
- 文件大小：最大500MB
- 拖拽或点击上传

### 2. 参数配置
- **置信度阈值**: 控制检测敏感度 (0.1-0.9)
- **IOU阈值**: 控制重叠检测过滤 (0.1-0.9)

### 3. 检测过程
- 实时进度显示
- 自动状态更新
- 错误处理与重试

### 4. 结果分析
- 跌倒事件统计
- 风险等级评估
- AI智能建议
- 数据可视化图表

## 🔧 API接口

### 上传视频
```
POST /upload
Content-Type: multipart/form-data
Body: video file
```

### 开始检测
```
POST /detect/{task_id}
Content-Type: application/json
Body: {"confidence": 0.5, "iou_threshold": 0.4}
```

### 查询状态
```
GET /status/{task_id}
```

### 获取结果
```
GET /result/{task_id}
```

### 下载视频
```
GET /download/{task_id}
```

## 📊 检测结果结构

```json
{
  "video_info": {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "total_frames": 3600,
    "duration": 120.0
  },
  "fall_events": [
    {
      "frame": 1500,
      "timestamp": 50.0,
      "type": "sudden",
      "confidence": 0.85,
      "bbox": [100, 200, 300, 400],
      "center": [200, 300]
    }
  ],
  "analysis": {
    "summary": {
      "total_falls": 2,
      "risk_level": "medium",
      "video_duration": 120.0,
      "processing_time": 45.2
    },
    "recommendations": [
      "⚠️ 检测到中等风险，需要关注",
      "👥 建议家属或护理人员定期检查"
    ]
  },
  "llm_analysis": "基于检测结果的智能分析..."
}
```

## 🎯 技术亮点

### 1. 高精度检测
- **双重检测机制**: 结合突发性和持续性跌倒识别
- **姿态关键点**: 17个关键点精确追踪
- **时序分析**: 滑动窗口投票机制

### 2. 智能分析
- **风险评估**: 基于事件频次和置信度的多维评估
- **个性化建议**: LLaMA模型生成的自然语言反馈
- **趋势分析**: 时间分布和模式识别

### 3. 用户体验
- **响应式设计**: 支持桌面和移动设备
- **实时反馈**: WebSocket实时进度更新
- **直观可视化**: Chart.js交互式图表

## 🛡️ 安全特性

- **本地计算**: 视频不上传云端
- **隐私保护**: 仅保存分析结果
- **数据清理**: 自动清理临时文件
- **错误处理**: 完善的异常处理机制

## 📈 性能优化

- **异步处理**: 后台任务队列
- **内存管理**: 大文件分块处理
- **模型优化**: 轻量化YOLO模型
- **缓存机制**: 智能结果缓存

## 🔮 未来规划

- [ ] 批量视频处理
- [ ] 实时摄像头监控
- [ ] 移动端APP
- [ ] 云端部署版本
- [ ] 多语言支持
- [ ] 高级数据分析

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持与反馈

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件反馈

---

**智能跌倒检测Web系统** - 守护长者安全，AI赋能关怀 💖
