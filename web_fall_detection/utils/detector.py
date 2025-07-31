"""
跌倒检测器 - 封装main.py的检测逻辑为Web友好的类
"""

import os
import sys
import cv2
import time
import json
import numpy as np
from collections import deque
from ultralytics import YOLO
from llama_cpp import Llama

# 添加父目录以导入main模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FallDetector:
    def __init__(self, fall_model_path='../models/best.pt', 
                 pose_model_path='../models/yolov8n-pose.pt',
                 llm_model_path='../models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
                 use_gpu=True, skip_frames=3):
        """
        初始化跌倒检测器
        
        Args:
            fall_model_path: YOLO跌倒检测模型路径
            pose_model_path: YOLO姿态检测模型路径
            llm_model_path: LLaMA模型路径
            use_gpu: 是否使用GPU加速
            skip_frames: 跳帧间隔（1=每帧检测，2=每2帧检测1次，3=每3帧检测1次）
        """
        self.fall_model_path = fall_model_path
        self.pose_model_path = pose_model_path
        self.llm_model_path = llm_model_path
        self.use_gpu = use_gpu
        self.skip_frames = max(1, skip_frames)  # 至少为1
        
        # 检查GPU可用性
        self.device = self._check_gpu_availability()
        
        # 初始化模型
        self._load_models()
        
        # 检测参数
        self.window_size = 30
        self.vote_threshold = 10
        self.speed_threshold = 20
        self.fall_velocity_threshold = 20
        self.fall_downward_threshold = 15
        
        # 性能统计
        self.performance_stats = {
            'frames_processed': 0,
            'frames_skipped': 0,
            'detection_time': 0,
            'total_processing_time': 0
        }
        
        
    def _check_gpu_availability(self):
        """检查GPU可用性并选择设备"""
        try:
            import torch
            if self.use_gpu and torch.cuda.is_available():
                device = 'cuda'
                gpu_name = torch.cuda.get_device_name(0)
                print(f"🚀 GPU加速已启用: {gpu_name}")
            else:
                device = 'cpu'
                if self.use_gpu:
                    print("⚠️ GPU不可用，使用CPU运行")
                else:
                    print("💻 使用CPU运行")
            return device
        except ImportError:
            print("⚠️ PyTorch未安装，使用CPU运行")
            return 'cpu'
    
    def _load_models(self):
        """加载所有模型"""
        try:
            print("🔄 正在加载模型...")
            
            # 加载YOLO模型并设置设备
            self.fall_model = YOLO(self.fall_model_path)
            self.pose_model = YOLO(self.pose_model_path)
            
            # 设置模型设备
            if hasattr(self.fall_model, 'to'):
                self.fall_model.to(self.device)
            if hasattr(self.pose_model, 'to'):
                self.pose_model.to(self.device)
                
            print(f"✅ YOLO模型加载完成 (设备: {self.device})")
            print(f"⚡ 跳帧设置: 每{self.skip_frames}帧检测1次")
            
            # 加载LLaMA模型
            if os.path.exists(self.llm_model_path):
                self.llm = Llama(
                    model_path=self.llm_model_path,
                    n_ctx=512,
                    verbose=False
                )
                print("✅ LLaMA模型加载完成")
            else:
                self.llm = None
                print("⚠️ LLaMA模型文件不存在，将跳过智能分析")
                
        except Exception as e:
            print(f"❌ 模型加载失败: {str(e)}")
            raise
    
    def detect_video(self, video_path, output_path, confidence=0.5, 
                    iou_threshold=0.4, progress_callback=None):
        """
        检测视频中的跌倒事件
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            confidence: 检测置信度阈值
            iou_threshold: IOU阈值
            progress_callback: 进度回调函数
            
        Returns:
            dict: 检测结果
        """
        start_time = time.time()
        cap = None
        out = None
        
        try:
            # 打开视频
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {video_path}")
            
            # 获取视频信息
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # 初始化视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # 检测状态
            fall_history = deque(maxlen=self.window_size)
            last_centers = []
            fall_events = []
            frame_count = 0
            error_count = 0
            max_errors = 50  # 最大允许错误数
            
            # 跳帧检测状态
            last_detection_result = (False, None)  # 缓存上次检测结果
            
            if progress_callback:
                progress_callback(0, "开始处理视频...")
            
            while True:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    frame_count += 1
                    
                    # 更新进度
                    if progress_callback and frame_count % 30 == 0:
                        progress = int((frame_count / total_frames) * 80)  # 80%用于检测
                        progress_callback(progress, f"正在处理第 {frame_count}/{total_frames} 帧... (跳帧:{self.skip_frames})")
                    
                    # 创建帧副本用于处理
                    display_frame = frame.copy()
                    
                    # 跌倒检测 - 跳帧优化
                    fall_detected = False
                    fall_info = None
                    
                    # 只在指定帧间隔进行检测
                    if frame_count % self.skip_frames == 1:  # 第1帧开始，然后每skip_frames帧检测一次
                        try:
                            detection_start = time.time()
                            fall_detected, fall_info = self._detect_fall_in_frame(
                                frame, last_centers, fall_history, frame_count
                            )
                            detection_time = time.time() - detection_start
                            
                            # 更新性能统计
                            self.performance_stats['frames_processed'] += 1
                            self.performance_stats['detection_time'] += detection_time
                            
                            # 缓存检测结果
                            last_detection_result = (fall_detected, fall_info)
                        except Exception as detection_error:
                            print(f"检测第{frame_count}帧时出错: {detection_error}")
                            error_count += 1
                            if error_count > max_errors:
                                print(f"错误过多({error_count})，停止处理")
                                break
                            # 继续处理下一帧
                            fall_detected = False
                            fall_info = None
                    else:
                        # 使用缓存的检测结果，统计跳过的帧
                        self.performance_stats['frames_skipped'] += 1
                        fall_detected, fall_info = last_detection_result
                    
                    # 记录跌倒事件（只在实际检测帧记录，避免重复）
                    if fall_detected and fall_info is not None and frame_count % self.skip_frames == 1:
                        try:
                            fall_events.append({
                                'frame': frame_count,
                                'timestamp': frame_count / fps,
                                'type': fall_info.get('type', 'unknown'),
                                'confidence': fall_info.get('confidence', 0.0),
                                'bbox': fall_info.get('bbox', []),
                                'center': fall_info.get('center', [])
                            })
                            print(f"⚠️ 检测到跌倒: 第{frame_count}帧 (跳帧模式)")
                        except Exception as event_error:
                            print(f"记录事件时出错: {event_error}")
                    
                    # 标注所有帧（即使使用缓存结果）
                    if fall_detected and fall_info is not None:
                        try:
                            self._annotate_frame(display_frame, fall_info)
                        except Exception as annotate_error:
                            print(f"标注第{frame_count}帧时出错: {annotate_error}")
                    
                    # 姿态检测 - 也应用跳帧优化
                    if frame_count % self.skip_frames == 1:
                        try:
                            self._detect_pose_in_frame(display_frame)
                        except Exception as pose_error:
                            print(f"姿态检测第{frame_count}帧时出错: {pose_error}")
                    
                    # 写入帧
                    try:
                        out.write(display_frame)
                    except Exception as write_error:
                        print(f"写入第{frame_count}帧时出错: {write_error}")
                    
                except Exception as frame_error:
                    print(f"处理第{frame_count}帧时出错: {frame_error}")
                    error_count += 1
                    if error_count > max_errors:
                        print(f"错误过多({error_count})，停止处理")
                        break
                    # 继续处理下一帧
                    continue
            
            if progress_callback:
                progress_callback(90, "生成智能分析...")
            
            # 生成智能分析
            llm_analysis = None
            try:
                llm_analysis = self._generate_llm_analysis(fall_events, video_path)
            except Exception as llm_error:
                print(f"LLM分析生成失败: {llm_error}")
                llm_analysis = "智能分析生成失败"
            
            processing_time = time.time() - start_time
            self.performance_stats['total_processing_time'] = processing_time
            
            # 计算性能指标
            avg_detection_time = (self.performance_stats['detection_time'] / 
                                 max(1, self.performance_stats['frames_processed']))
            speed_improvement = (self.performance_stats['frames_skipped'] + 
                               self.performance_stats['frames_processed']) / max(1, self.performance_stats['frames_processed'])
            
            if progress_callback:
                progress_callback(100, f"处理完成! 速度提升: {speed_improvement:.1f}x")
            
            print(f"⚡ 性能统计:")
            print(f"   - 实际检测帧数: {self.performance_stats['frames_processed']}")
            print(f"   - 跳过帧数: {self.performance_stats['frames_skipped']}")
            print(f"   - 平均检测耗时: {avg_detection_time*1000:.1f}ms/帧")
            print(f"   - 速度提升: {speed_improvement:.1f}倍")
            
            return {
                'video_info': {
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'total_frames': total_frames,
                    'duration': total_frames / fps
                },
                'fall_events': fall_events,
                'llm_analysis': llm_analysis,
                'processing_time': processing_time,
                'output_path': output_path,
                'error_count': error_count,
                'performance_stats': {
                    'frames_processed': self.performance_stats['frames_processed'],
                    'frames_skipped': self.performance_stats['frames_skipped'],
                    'avg_detection_time': avg_detection_time,
                    'speed_improvement': speed_improvement,
                    'device_used': self.device
                }
            }
            
        except Exception as e:
            print(f"视频处理失败: {str(e)}")
            raise e
            
        finally:
            # 确保资源被正确释放
            try:
                if cap is not None:
                    cap.release()
                if out is not None:
                    out.release()
                cv2.destroyAllWindows()
            except Exception as cleanup_error:
                print(f"清理资源时出错: {cleanup_error}")
    
    def _detect_fall_in_frame(self, frame, last_centers, fall_history, frame_count):
        """在单帧中检测跌倒"""
        try:
            # 使用设备加速预测
            fall_results = self.fall_model.predict(
                source=frame, 
                conf=0.50, 
                iou=0.4, 
                device=self.device,
                verbose=False  # 减少输出噪音
            )[0]
            
            current_fall_centers = []
            current_fall_count = 0
            sudden_fall_flag = False
            fall_info = None
            
            # 安全检查预测结果
            if fall_results is None:
                return False, None
                
            if fall_results.boxes is not None and len(fall_results.boxes) > 0:
                for i, box in enumerate(fall_results.boxes):
                    try:
                        # 安全获取类别和置信度
                        if box.cls is None or len(box.cls) == 0:
                            continue
                        if box.conf is None or len(box.conf) == 0:
                            continue
                        if box.xyxy is None or len(box.xyxy) == 0:
                            continue
                            
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        # 安全获取边界框坐标
                        xyxy = box.xyxy[0]
                        if len(xyxy) < 4:
                            continue
                            
                        x1, y1, x2, y2 = map(int, xyxy)
                        
                        # 验证坐标的有效性
                        if x1 >= x2 or y1 >= y2 or x1 < 0 or y1 < 0:
                            continue
                            
                        center = self._compute_center((x1, y1, x2, y2))
                        if center is None or len(center) != 2:
                            continue
                            
                        current_fall_centers.append(center)
                        
                        if cls_id in [0, 1]:  # 跌倒类别
                            current_fall_count += 1
                            fall_info = {
                                'confidence': conf,
                                'bbox': [x1, y1, x2, y2],
                                'center': center,
                                'type': 'sustained'
                            }
                    except Exception as box_error:
                        print(f"处理第{i}个边界框时出错: {box_error}")
                        continue
            
            # 安全更新跌倒历史
            try:
                fall_history.append(current_fall_count > 0)
                persistent_fall = sum(fall_history) >= self.vote_threshold
            except Exception as history_error:
                print(f"更新跌倒历史时出错: {history_error}")
                persistent_fall = False
            
            # 安全检测突发跌倒
            try:
                if (len(last_centers) > 0 and len(current_fall_centers) > 0 and
                    isinstance(last_centers, list) and isinstance(current_fall_centers, list)):
                    
                    for i in range(min(len(current_fall_centers), len(last_centers))):
                        if (i < len(current_fall_centers) and i < len(last_centers) and
                            current_fall_centers[i] is not None and last_centers[i] is not None):
                            
                            center_now = current_fall_centers[i]
                            center_prev = last_centers[i]
                            
                            # 验证中心点数据
                            if (len(center_now) >= 2 and len(center_prev) >= 2 and
                                all(isinstance(x, (int, float)) for x in center_now) and
                                all(isinstance(x, (int, float)) for x in center_prev)):
                                
                                velocity = self._compute_velocity(center_now, center_prev)
                                delta_y = center_now[1] - center_prev[1]
                                
                                if (velocity > self.fall_velocity_threshold and 
                                    delta_y > self.fall_downward_threshold):
                                    sudden_fall_flag = True
                                    if fall_info is None:
                                        fall_info = {
                                            'confidence': 0.8,
                                            'bbox': [int(center_now[0]-50), int(center_now[1]-50), 
                                                    int(center_now[0]+50), int(center_now[1]+50)],
                                            'center': center_now,
                                            'type': 'sudden'
                                        }
                                    else:
                                        fall_info['type'] = 'sudden'
                                    break
            except Exception as sudden_error:
                print(f"检测突发跌倒时出错: {sudden_error}")
                sudden_fall_flag = False
            
            # 安全更新中心点历史
            try:
                if isinstance(last_centers, list):
                    last_centers.clear()
                    last_centers.extend(current_fall_centers)
            except Exception as center_error:
                print(f"更新中心点历史时出错: {center_error}")
            
            # 返回检测结果
            fall_detected = persistent_fall or sudden_fall_flag
            return fall_detected, fall_info
            
        except Exception as e:
            print(f"帧检测错误: {str(e)}")
            return False, None
    
    def _detect_pose_in_frame(self, frame):
        """在帧中检测姿态关键点"""
        try:
            pose_results = self.pose_model.predict(
                source=frame, 
                conf=0.25,
                device=self.device,
                verbose=False  # 减少输出噪音
            )[0]
            
            if pose_results.keypoints is not None and len(pose_results.keypoints) > 0:
                for kpts in pose_results.keypoints.xy:
                    if kpts is not None and len(kpts) > 0:
                        for x, y in kpts:
                            if x > 0 and y > 0:  # 只绘制有效关键点
                                cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 0), -1)
        except Exception as e:
            print(f"姿态检测错误: {str(e)}")
            # 继续处理，不中断视频处理
            pass
    
    def _annotate_frame(self, frame, fall_info):
        """在帧上标注跌倒信息"""
        try:
            if fall_info and all(key in fall_info for key in ['bbox', 'confidence', 'type']):
                x1, y1, x2, y2 = fall_info['bbox']
                conf = fall_info['confidence']
                fall_type = fall_info['type']
                
                # 绘制边界框
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                
                # 添加文本标注
                text = f"FALL ({fall_type.upper()}) {conf:.2f}"
                cv2.putText(frame, text, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # 添加警告文本
                warning_text = "ALERT: Fall Detected!"
                cv2.putText(frame, warning_text, (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        except Exception as e:
            print(f"标注错误: {str(e)}")
            # 继续处理，不中断视频处理
            pass
    
    def _generate_llm_analysis(self, fall_events, video_path):
        """生成LLM智能分析"""
        if not self.llm or not fall_events:
            return None
        
        try:
            # 限制分析的事件数量，避免token超限
            max_events = 10
            limited_events = fall_events[:max_events] if len(fall_events) > max_events else fall_events
            
            # 构建详细的分析数据
            analysis_data = {
                "total_falls": len(fall_events),
                "sample_events": len(limited_events),
                "fall_types": list(set([event.get('type', 'unknown') for event in limited_events])),
                "confidence_stats": {
                    "max": max([event.get('confidence', 0) for event in limited_events], default=0),
                    "min": min([event.get('confidence', 0) for event in limited_events], default=0),
                    "avg": sum([event.get('confidence', 0) for event in limited_events]) / len(limited_events) if limited_events else 0
                },
                "time_distribution": {
                    "first_event": min([event.get('timestamp', 0) for event in limited_events], default=0),
                    "last_event": max([event.get('timestamp', 0) for event in limited_events], default=0),
                    "time_span": max([event.get('timestamp', 0) for event in limited_events], default=0) - min([event.get('timestamp', 0) for event in limited_events], default=0)
                }
            }
            
            # 构建更详细的提示词
            prompt = f"""你是一名专业的老年护理顾问。根据以下跌倒检测数据，提供专业的护理建议：

检测结果摘要：
- 总跌倒次数：{analysis_data['total_falls']}次
- 跌倒类型：{', '.join(analysis_data['fall_types'])}
- 检测置信度：最高{analysis_data['confidence_stats']['max']:.2f}，最低{analysis_data['confidence_stats']['min']:.2f}，平均{analysis_data['confidence_stats']['avg']:.2f}
- 时间跨度：{analysis_data['time_distribution']['time_span']:.1f}秒

请从以下几个方面提供专业建议：

1. 风险评估：基于跌倒次数和类型评估风险等级（低/中/高）
2. 即时措施：当前应该采取的紧急措施
3. 预防建议：未来如何预防类似事件
4. 环境改善：居住环境安全优化建议
5. 医疗建议：是否需要寻求专业医疗帮助

请用中文回答，语言温和关怀，建议具体可行。每个方面用简短的句子说明。"""
            
            # 生成分析 - 增加token数以获得更详细的回答
            response = self.llm(prompt, max_tokens=300, stop=["</s>"], temperature=0.7)
            analysis_text = response["choices"][0]["text"].strip()
            
            # 如果回答太短，提供备用分析
            if len(analysis_text) < 50:
                return self._generate_fallback_analysis(analysis_data)
            
            return analysis_text
            
        except Exception as e:
            print(f"LLM分析生成失败: {str(e)}")
            return self._generate_fallback_analysis({
                "total_falls": len(fall_events),
                "fall_types": list(set([event.get('type', 'unknown') for event in fall_events]))
            })
    
    def _generate_fallback_analysis(self, analysis_data):
        """生成备用分析（当LLM不可用时）"""
        total_falls = analysis_data.get('total_falls', 0)
        fall_types = analysis_data.get('fall_types', [])
        
        if total_falls == 0:
            return """智能分析：
            
风险评估：低风险 ✅
当前状态良好，未检测到跌倒事件。

预防建议：
• 保持定期运动，增强身体平衡能力
• 定期检查居住环境安全
• 保持良好的照明条件

环境建议：
• 移除地面障碍物和松散地毯
• 安装扶手和防滑垫
• 确保通道畅通"""
        
        elif total_falls <= 2:
            risk = "中等风险"
            immediate = "建议加强监护，评估跌倒原因"
        else:
            risk = "高风险"
            immediate = "建议立即寻求医疗帮助，安排专业护理"
        
        type_advice = ""
        if 'sudden' in fall_types:
            type_advice += "\n• 突发性跌倒可能与平衡或协调问题有关"
        if 'sustained' in fall_types:
            type_advice += "\n• 持续性跌倒可能与起身困难有关"
        
        return f"""智能分析：

风险评估：{risk} ⚠️
检测到{total_falls}次跌倒事件，需要关注。

即时措施：
{immediate}

预防建议：
• 加强身体锻炼，特别是平衡训练
• 定期体检，关注可能的健康问题
• 考虑使用辅助设备（拐杖、助行器）{type_advice}

环境改善：
• 立即检查和改善居住环境
• 增加照明，移除障碍物
• 考虑安装紧急呼叫设备

医疗建议：
• 建议咨询医生进行全面评估
• 可能需要物理治疗或康复训练"""
    
    def _compute_center(self, box):
        """计算边界框中心点"""
        try:
            if box is None or len(box) < 4:
                return None
            x1, y1, x2, y2 = box
            if not all(isinstance(coord, (int, float)) for coord in [x1, y1, x2, y2]):
                return None
            return ((x1 + x2) // 2, (y1 + y2) // 2)
        except Exception as e:
            print(f"计算中心点时出错: {e}")
            return None
    
    def _compute_velocity(self, p1, p2):
        """计算两点间速度"""
        try:
            if (p1 is None or p2 is None or 
                len(p1) < 2 or len(p2) < 2 or
                not all(isinstance(coord, (int, float)) for coord in p1) or
                not all(isinstance(coord, (int, float)) for coord in p2)):
                return 0
            return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        except Exception as e:
            print(f"计算速度时出错: {e}")
            return 0
