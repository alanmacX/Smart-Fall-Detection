"""
智能跌倒检测Web系统 - Flask主应用
集成YOLO姿态检测和LLaMA智能分析的Web端跌倒检测系统
"""

import os
import sys
import uuid
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
from werkzeug.serving import make_server
import cv2

# 添加父目录到路径以导入main模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 检查是否能导入工具模块，如果不能则使用演示模式
try:
    from utils.detector import FallDetector
    from utils.analyzer import ResultAnalyzer
    DEMO_MODE = False
except ImportError:
    print("⚠️ 主检测模块不可用，切换到演示模式")
    from utils.demo import DemoDetector as FallDetector
    from utils.demo import DemoAnalyzer as ResultAnalyzer
    DEMO_MODE = True

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fall-detection-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# 性能配置
PERFORMANCE_CONFIG = {
    'use_gpu': True,       # 是否使用GPU加速
    'skip_frames': 3,      # 跳帧间隔（1=每帧检测，3=每3帧检测）
    'detection_conf': 0.5, # 检测置信度阈值
    'iou_threshold': 0.4   # IOU阈值
}

# 全局任务存储
tasks = {}

# 使用绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'static', 'outputs')

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print(f"📁 上传目录: {UPLOAD_FOLDER}")
print(f"📁 输出目录: {OUTPUT_FOLDER}")

class TaskStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@app.route('/')
def index():
    """主页 - 视频上传界面"""
    return render_template('index.html')

@app.route('/test')
def test_upload():
    """测试上传页面"""
    return render_template('test_upload.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    """处理视频上传"""
    try:
        print("📤 开始处理视频上传...")
        
        if 'video' not in request.files:
            print("❌ 请求中没有video字段")
            return jsonify({'error': '没有选择视频文件'}), 400
        
        file = request.files['video']
        if file.filename == '':
            print("❌ 文件名为空")
            return jsonify({'error': '没有选择文件'}), 400
        
        print(f"📝 上传文件: {file.filename}")
        print(f"📏 文件大小: {len(file.read())} bytes")
        file.seek(0)  # 重置文件指针
        
        if not allowed_file(file.filename):
            print(f"❌ 不支持的文件格式: {file.filename}")
            return jsonify({'error': '不支持的视频格式，请上传mp4、avi或mov文件'}), 400
        
        # 生成唯一任务ID
        task_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"{task_id}_{filename}")
        
        print(f"💾 保存路径: {filepath}")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 保存文件
        file.save(filepath)
        
        # 验证文件是否保存成功
        if not os.path.exists(filepath):
            print(f"❌ 文件保存失败: {filepath}")
            return jsonify({'error': '文件保存失败'}), 500
        
        file_size = os.path.getsize(filepath)
        print(f"✅ 文件保存成功，大小: {file_size} bytes")
        
        # 初始化任务状态
        tasks[task_id] = {
            'id': task_id,
            'status': TaskStatus.PENDING,
            'filename': filename,
            'filepath': filepath,
            'upload_time': datetime.now().isoformat(),
            'progress': 0,
            'message': '视频上传成功，等待处理...',
            'result': None
        }
        
        print(f"✅ 任务创建成功: {task_id}")
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '视频上传成功',
            'filename': filename
        })
        
    except Exception as e:
        print(f"❌ 上传错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/detect/<task_id>', methods=['POST'])
def start_detection(task_id):
    """开始检测任务"""
    try:
        if task_id not in tasks:
            return jsonify({'error': '任务不存在'}), 404
        
        task = tasks[task_id]
        if task['status'] != TaskStatus.PENDING:
            return jsonify({'error': '任务已在处理中或已完成'}), 400
        
        # 获取检测参数
        params = request.get_json() or {}
        confidence = params.get('confidence', 0.5)
        iou_threshold = params.get('iou_threshold', 0.4)
        
        # 更新任务状态
        task['status'] = TaskStatus.PROCESSING
        task['progress'] = 0
        task['message'] = '开始检测处理...'
        task['start_time'] = datetime.now().isoformat()
        
        # 在后台线程中运行检测
        detection_thread = threading.Thread(
            target=run_detection_task,
            args=(task_id, confidence, iou_threshold),
            daemon=True
        )
        detection_thread.start()
        
        return jsonify({
            'success': True,
            'message': '检测任务已启动',
            'task_id': task_id
        })
        
    except Exception as e:
        return jsonify({'error': f'启动检测失败: {str(e)}'}), 500

@app.route('/status/<task_id>')
def get_task_status(task_id):
    """获取任务状态"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = tasks[task_id]
    return jsonify({
        'task_id': task_id,
        'status': task['status'],
        'progress': task['progress'],
        'message': task['message'],
        'result': task.get('result')
    })

@app.route('/result/<task_id>')
def get_result(task_id):
    """获取检测结果详情"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = tasks[task_id]
    if task['status'] != TaskStatus.COMPLETED:
        return jsonify({'error': '任务尚未完成'}), 400
    
    return render_template('result.html', 
                         task_id=task_id, 
                         result=task['result'],
                         task=task)

@app.route('/download/<task_id>')
def download_result(task_id):
    """下载处理后的视频"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = tasks[task_id]
    if task['status'] != TaskStatus.COMPLETED or not task['result']:
        return jsonify({'error': '结果文件不存在'}), 404
    
    output_path = task['result'].get('output_video_path')
    if not output_path or not os.path.exists(output_path):
        return jsonify({'error': '输出视频文件不存在'}), 404
    
    try:
        return send_file(
            output_path, 
            as_attachment=False,  # 改为False以支持在线预览
            download_name=f"detection_result_{task['filename']}",
            mimetype='video/mp4'  # 明确指定MIME类型
        )
    except Exception as e:
        print(f"发送文件失败: {str(e)}")
        return jsonify({'error': f'文件发送失败: {str(e)}'}), 500

@app.route('/preview/<task_id>')
def preview_result(task_id):
    """预览处理后的视频（用于在线播放）"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = tasks[task_id]
    if task['status'] != TaskStatus.COMPLETED or not task['result']:
        return jsonify({'error': '结果文件不存在'}), 404
    
    output_path = task['result'].get('output_video_path')
    if not output_path or not os.path.exists(output_path):
        return jsonify({'error': '输出视频文件不存在'}), 404
    
    try:
        # 创建响应，添加必要的headers支持视频流
        response = send_file(
            output_path, 
            as_attachment=False,
            mimetype='video/mp4',
            conditional=True  # 支持范围请求，对视频播放很重要
        )
        
        # 添加CORS头和缓存控制
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Cache-Control'] = 'no-cache'
        
        return response
    except Exception as e:
        print(f"预览文件失败: {str(e)}")
        return jsonify({'error': f'文件预览失败: {str(e)}'}), 500

@app.route('/video/<task_id>')
def serve_video(task_id):
    """直接服务视频文件（静态文件方式）"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = tasks[task_id]
    if task['status'] != TaskStatus.COMPLETED or not task['result']:
        return jsonify({'error': '结果文件不存在'}), 404
    
    output_path = task['result'].get('output_video_path')
    if not output_path or not os.path.exists(output_path):
        return jsonify({'error': '输出视频文件不存在'}), 404
    
    # 使用静态文件方式服务
    try:
        from flask import Response
        
        def generate():
            with open(output_path, 'rb') as f:
                data = f.read(1024)
                while data:
                    yield data
                    data = f.read(1024)
        
        response = Response(generate(), mimetype='video/mp4')
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Cache-Control', 'no-cache')
        response.headers.add('Access-Control-Allow-Origin', '*')
        
        return response
        
    except Exception as e:
        print(f"服务视频文件失败: {str(e)}")
        return jsonify({'error': f'文件服务失败: {str(e)}'}), 500

@app.route('/debug/task/<task_id>')
def debug_task(task_id):
    """调试任务状态（开发用）"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = tasks[task_id]
    
    # 检查输出文件
    output_path = task.get('result', {}).get('output_video_path')
    file_info = {}
    if output_path:
        file_info = {
            'path': output_path,
            'exists': os.path.exists(output_path),
            'size': os.path.getsize(output_path) if os.path.exists(output_path) else 0,
            'absolute_path': os.path.abspath(output_path)
        }
    
    return jsonify({
        'task_id': task_id,
        'task': task,
        'file_info': file_info,
        'output_folder': OUTPUT_FOLDER,
        'upload_folder': UPLOAD_FOLDER
    })

@app.route('/api/tasks')
def list_tasks():
    """获取所有任务列表"""
    task_list = []
    for task_id, task in tasks.items():
        task_list.append({
            'id': task_id,
            'filename': task['filename'],
            'status': task['status'],
            'upload_time': task['upload_time'],
            'progress': task['progress']
        })
    
    # 按上传时间排序
    task_list.sort(key=lambda x: x['upload_time'], reverse=True)
    return jsonify({
        'success': True,
        'tasks': task_list,
        'performance': PERFORMANCE_CONFIG
    })

@app.route('/api/performance', methods=['GET', 'POST'])
def handle_performance_config():
    """处理性能配置"""
    global PERFORMANCE_CONFIG
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'config': PERFORMANCE_CONFIG,
            'info': {
                'skip_frames_effect': f"每{PERFORMANCE_CONFIG['skip_frames']}帧检测1次 (速度提升约{PERFORMANCE_CONFIG['skip_frames']}倍)",
                'gpu_status': "启用GPU加速" if PERFORMANCE_CONFIG['use_gpu'] else "使用CPU计算"
            }
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # 更新配置
            if 'use_gpu' in data:
                PERFORMANCE_CONFIG['use_gpu'] = bool(data['use_gpu'])
            if 'skip_frames' in data:
                PERFORMANCE_CONFIG['skip_frames'] = max(1, int(data['skip_frames']))
            if 'detection_conf' in data:
                PERFORMANCE_CONFIG['detection_conf'] = max(0.1, min(1.0, float(data['detection_conf'])))
            if 'iou_threshold' in data:
                PERFORMANCE_CONFIG['iou_threshold'] = max(0.1, min(1.0, float(data['iou_threshold'])))
            
            return jsonify({
                'success': True,
                'message': '性能配置已更新',
                'config': PERFORMANCE_CONFIG
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'配置更新失败: {str(e)}'
            }), 400

def run_detection_task(task_id, confidence=0.5, iou_threshold=0.4):
    """在后台运行检测任务"""
    try:
        task = tasks[task_id]
        print(f"🔄 开始处理任务 {task_id}")
        print(f"📁 输入文件: {task['filepath']}")
        
        # 确保输出目录存在
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        print(f"📁 输出目录: {OUTPUT_FOLDER}")
        
        # 初始化检测器
        if DEMO_MODE:
            print("⚠️ 使用演示模式检测器")
            detector = FallDetector()
        else:
            print("✅ 使用真实AI模型检测器")
            # 使用全局性能配置
            detector = FallDetector(
                fall_model_path='../models/best.pt',
                pose_model_path='../models/yolov8n-pose.pt',
                llm_model_path='../models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
                use_gpu=PERFORMANCE_CONFIG['use_gpu'],
                skip_frames=PERFORMANCE_CONFIG['skip_frames']
            )
            print(f"⚡ 性能优化: GPU={PERFORMANCE_CONFIG['use_gpu']}, 跳帧={PERFORMANCE_CONFIG['skip_frames']}")
        
        # 设置进度回调
        def progress_callback(progress, message):
            tasks[task_id]['progress'] = progress
            tasks[task_id]['message'] = message
            print(f"📊 任务 {task_id} 进度: {progress}% - {message}")
        
        # 运行检测
        output_path = os.path.join(OUTPUT_FOLDER, f"result_{task_id}.mp4")
        print(f"📹 输出路径: {output_path}")
        
        result = detector.detect_video(
            video_path=task['filepath'],
            output_path=output_path,
            confidence=PERFORMANCE_CONFIG['detection_conf'],
            iou_threshold=PERFORMANCE_CONFIG['iou_threshold'],
            progress_callback=progress_callback
        )
        
        print(f"✅ 检测完成，开始分析结果...")
        
        # 检查输出文件是否生成
        if not os.path.exists(output_path):
            raise Exception(f"输出视频文件未生成: {output_path}")
        
        file_size = os.path.getsize(output_path)
        print(f"📹 输出视频文件大小: {file_size} bytes")
        
        if file_size == 0:
            raise Exception("输出视频文件为空")
        
        # 分析结果
        if DEMO_MODE:
            from utils.demo import DemoAnalyzer
            analyzer = DemoAnalyzer()
        else:
            analyzer = ResultAnalyzer()
            
        analysis = analyzer.analyze_detection_result(result)
        
        # 更新任务状态
        task['status'] = TaskStatus.COMPLETED
        task['progress'] = 100
        task['message'] = '检测完成'
        task['end_time'] = datetime.now().isoformat()
        task['result'] = {
            'detection_data': result,
            'analysis': analysis,
            'output_video_path': output_path,
            'summary': {
                'total_frames': result.get('total_frames', 0),
                'fall_events': len(result.get('fall_events', [])),
                'max_confidence': max([e.get('confidence', 0) for e in result.get('fall_events', [])], default=0),
                'processing_time': result.get('processing_time', 0),
                'output_file_size': file_size
            }
        }
        
        print(f"🎉 任务 {task_id} 完成成功")
        print(f"📊 检测结果: {len(result.get('fall_events', []))} 个跌倒事件")
        
    except Exception as e:
        # 错误处理
        print(f"❌ 任务 {task_id} 检测失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        tasks[task_id]['status'] = TaskStatus.ERROR
        tasks[task_id]['message'] = f'检测失败: {str(e)}'
        tasks[task_id]['error'] = str(e)
        tasks[task_id]['end_time'] = datetime.now().isoformat()

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'error': '文件过大，请上传小于500MB的视频文件'}), 413

@app.errorhandler(500)
def internal_error(e):
    """服务器内部错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 智能跌倒检测Web系统启动中...")
    print("=" * 60)
    print("📍 访问地址: http://localhost:5000")
    print("📊 功能特性:")
    print("   ✓ 视频上传与处理")
    print("   ✓ 智能跌倒检测")
    print("   ✓ LLM分析建议")
    print("   ✓ 实时进度监控")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
