"""
演示检测器 - 当模型文件不可用时的备用方案
生成模拟的检测结果用于系统演示
"""

import time
import random
import json
import os
import cv2
from datetime import datetime

class DemoDetector:
    """演示用的检测器，生成模拟检测结果"""
    
    def __init__(self, *args, **kwargs):
        self.is_demo = True
        print("⚠️ 使用演示模式 - 将生成模拟检测结果")
    
    def detect_video(self, video_path, output_path, confidence=0.5, 
                    iou_threshold=0.4, progress_callback=None):
        """
        模拟视频检测过程
        """
        try:
            start_time = time.time()
            
            # 获取视频信息
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {video_path}")
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            # 创建输出视频（复制原视频并添加演示标识）
            # 使用H.264编码器，更好的浏览器兼容性
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264编码
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # 如果H.264失败，尝试其他编码器
            if not out.isOpened():
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                
            # 如果还是失败，尝试默认编码器
            if not out.isOpened():
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                # 临时输出为avi，然后转换为mp4
                temp_output = output_path.replace('.mp4', '_temp.avi')
                out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))
            
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # 更新进度
                if progress_callback and frame_count % 30 == 0:
                    progress = int((frame_count / total_frames) * 90)
                    progress_callback(progress, f"演示模式处理第 {frame_count}/{total_frames} 帧...")
                
                # 添加演示标识
                cv2.putText(frame, "DEMO MODE", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
                # 模拟跌倒检测标注（随机在某些帧上）
                if random.random() < 0.02:  # 2%的概率
                    # 绘制模拟检测框
                    x1, y1 = random.randint(50, width//2), random.randint(50, height//2)
                    x2, y2 = x1 + random.randint(100, 200), y1 + random.randint(150, 300)
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"FALL DETECTED (Demo)", (x1, y1-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                out.write(frame)
            
            cap.release()
            out.release()
            
            # 如果使用了临时文件，需要转换为mp4
            temp_output = output_path.replace('.mp4', '_temp.avi')
            if os.path.exists(temp_output):
                import subprocess
                try:
                    # 使用ffmpeg转换（如果可用）
                    subprocess.run([
                        'ffmpeg', '-i', temp_output, 
                        '-c:v', 'libx264', '-c:a', 'aac',
                        '-y', output_path
                    ], check=True, capture_output=True)
                    os.remove(temp_output)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # ffmpeg不可用，重命名文件
                    os.rename(temp_output, output_path)
            
            # 验证输出文件
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise Exception("视频文件生成失败或为空")
            
            if progress_callback:
                progress_callback(95, "生成演示分析结果...")
            
            # 生成模拟检测结果
            fall_events = self._generate_demo_events(duration, fps)
            llm_analysis = self._generate_demo_analysis(fall_events)
            
            processing_time = time.time() - start_time
            
            if progress_callback:
                progress_callback(100, "演示检测完成!")
            
            return {
                'video_info': {
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'total_frames': total_frames,
                    'duration': duration
                },
                'fall_events': fall_events,
                'llm_analysis': llm_analysis,
                'processing_time': processing_time,
                'output_path': output_path,
                'demo_mode': True
            }
            
        except Exception as e:
            raise Exception(f"演示检测失败: {str(e)}")
    
    def _generate_demo_events(self, duration, fps):
        """生成模拟跌倒事件"""
        events = []
        
        # 根据视频时长生成合理数量的事件
        event_count = random.randint(0, max(1, int(duration // 30)))  # 平均每30秒最多1个事件
        
        for i in range(event_count):
            timestamp = random.uniform(10, duration - 10)  # 避免在开头结尾
            frame = int(timestamp * fps)
            
            event = {
                'frame': frame,
                'timestamp': timestamp,
                'type': random.choice(['sudden', 'sustained']),
                'confidence': random.uniform(0.6, 0.95),
                'bbox': [
                    random.randint(50, 200),
                    random.randint(50, 200),
                    random.randint(250, 400),
                    random.randint(250, 400)
                ],
                'center': [random.randint(150, 300), random.randint(150, 300)]
            }
            events.append(event)
        
        # 按时间排序
        events.sort(key=lambda x: x['timestamp'])
        return events
    
    def _generate_demo_analysis(self, fall_events):
        """生成模拟LLM分析"""
        if not fall_events:
            return """演示模式 - AI智能分析：

🔍 风险评估：低风险
✅ 视频分析未发现跌倒事件，整体状态良好。

� 预防建议：
• 继续保持良好的居家安全习惯
• 定期进行简单的平衡训练
• 保持适量运动，增强身体协调性

🏠 环境优化：
• 确保居住空间照明充足
• 定期检查地面是否有障碍物
• 保持通道畅通，避免杂物堆积

📊 后续监护：
• 建议定期使用系统进行安全检查
• 保持与家人的定期联系
• 如有身体不适，及时就医

注意：这是演示模式生成的模拟结果，实际使用时将采用真实的AI模型进行分析。"""
        
        fall_count = len(fall_events)
        fall_types = [e['type'] for e in fall_events]
        sudden_count = fall_types.count('sudden')
        sustained_count = fall_types.count('sustained')
        
        # 根据事件数量判断风险等级
        if fall_count <= 1:
            risk_level = "低风险"
            risk_icon = "🟢"
            immediate_action = "建议加强日常观察"
        elif fall_count <= 3:
            risk_level = "中等风险"
            risk_icon = "🟡"
            immediate_action = "建议增加监护和安全措施"
        else:
            risk_level = "高风险"
            risk_icon = "🔴"
            immediate_action = "建议立即寻求专业医疗帮助"
        
        # 计算模拟的平均置信度
        confidences = [e['confidence'] for e in fall_events]
        avg_confidence = sum(confidences) / len(confidences)
        
        analysis = f"""演示模式 - AI智能分析：

🔍 风险评估：{risk_icon} {risk_level}
检测到{fall_count}次跌倒事件，平均检测置信度：{avg_confidence:.1%}
   - 突发性跌倒：{sudden_count}次
   - 持续性跌倒：{sustained_count}次

⚡ 即时措施：
{immediate_action}
"""
        
        if fall_count <= 2:
            analysis += """
💡 护理建议：
• 增加居家安全措施，如安装扶手和防滑垫
• 考虑寻求家属或护理人员的协助
• 定期进行身体检查，关注平衡能力
• 如有需要可咨询医疗专业人员

🏠 环境改善：
• 移除地面松散物品和障碍物
• 改善室内照明条件
• 在卫生间和走廊安装扶手
• 考虑使用防滑鞋和合适的拐杖

� 后续监护：
• 建议家属增加探访频率
• 考虑安装紧急呼叫设备
• 定期使用本系统进行安全监测"""
        else:
            analysis += """
🚨 紧急建议：
• 立即联系家属或紧急联系人
• 强烈建议寻求专业医疗帮助
• 安排专业护理人员或家属陪护
• 立即评估和改善居住环境安全

🏥 医疗建议：
• 进行全面的身体和神经系统检查
• 评估药物副作用对跌倒的影响
• 考虑物理治疗和康复训练
• 可能需要住院观察或专业护理

📞 紧急联系：
• 建议建立24小时紧急联系机制
• 考虑安装医疗警报设备
• 安排专业护理人员定期上门"""
        
        # 根据跌倒类型添加特定建议
        if sudden_count > 0:
            analysis += f"""

⚡ 突发性跌倒专项建议：
• 可能与平衡、协调或突发健康问题有关
• 建议进行神经系统和心血管检查
• 考虑调整或评估当前用药情况
• 增加平衡训练和协调性练习"""
        
        if sustained_count > 0:
            analysis += f"""

🕐 持续性跌倒专项建议：
• 可能与肌力不足或起身困难有关
• 建议进行肌力评估和训练
• 考虑使用辅助起身设备
• 安排康复训练以改善活动能力"""
        
        analysis += "\n\n注意：这是演示模式生成的模拟结果，实际使用时将采用真实的AI模型进行更精准的分析。"
        
        return analysis


class DemoAnalyzer:
    """演示用的结果分析器"""
    
    def analyze_detection_result(self, detection_result):
        """分析检测结果"""
        fall_events = detection_result.get('fall_events', [])
        video_info = detection_result.get('video_info', {})
        
        if not fall_events:
            return self._generate_no_fall_analysis(video_info)
        
        # 基础统计
        total_falls = len(fall_events)
        fall_types = [event['type'] for event in fall_events]
        type_counts = {'sudden': 0, 'sustained': 0}
        for ft in fall_types:
            type_counts[ft] = type_counts.get(ft, 0) + 1
        
        # 置信度分析
        confidences = [event['confidence'] for event in fall_events]
        avg_conf = sum(confidences) / len(confidences)
        max_conf = max(confidences)
        min_conf = min(confidences)
        
        # 风险评估
        if total_falls <= 1:
            risk_level = 'low'
        elif total_falls <= 3:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        # 生成图表数据
        chart_data = {
            'timeline': [
                {
                    'timestamp': e['timestamp'],
                    'frame': e['frame'],
                    'confidence': e['confidence'],
                    'type': e['type']
                } for e in fall_events
            ],
            'confidence_trend': [
                {'x': i+1, 'y': e['confidence'], 'type': e['type']} 
                for i, e in enumerate(fall_events)
            ],
            'risk_heatmap': []
        }
        
        # 生成建议
        recommendations = self._generate_demo_recommendations(risk_level, total_falls, fall_types)
        
        # 生成时间线
        timeline = []
        for i, event in enumerate(fall_events):
            minutes = int(event['timestamp'] // 60)
            seconds = int(event['timestamp'] % 60)
            timeline.append({
                'id': i + 1,
                'time': f"{minutes:02d}:{seconds:02d}",
                'timestamp': event['timestamp'],
                'type': event['type'],
                'confidence': event['confidence'],
                'frame': event['frame'],
                'description': f"演示事件 {i+1} ({event['type']}类型)"
            })
        
        return {
            'summary': {
                'total_falls': total_falls,
                'risk_level': risk_level,
                'processing_time': detection_result.get('processing_time', 0),
                'video_duration': video_info.get('duration', 0)
            },
            'fall_types': {
                'sustained': type_counts.get('sustained', 0),
                'sudden': type_counts.get('sudden', 0),
                'distribution': type_counts
            },
            'time_analysis': {
                'peak_hours': [],
                'distribution': []
            },
            'confidence_analysis': {
                'average': avg_conf,
                'max': max_conf,
                'min': min_conf,
                'distribution': [
                    {'range': '0.6-0.7', 'count': len([c for c in confidences if 0.6 <= c < 0.7])},
                    {'range': '0.7-0.8', 'count': len([c for c in confidences if 0.7 <= c < 0.8])},
                    {'range': '0.8-0.9', 'count': len([c for c in confidences if 0.8 <= c < 0.9])},
                    {'range': '0.9-1.0', 'count': len([c for c in confidences if 0.9 <= c <= 1.0])}
                ]
            },
            'chart_data': chart_data,
            'recommendations': recommendations,
            'timeline': timeline,
            'demo_mode': True
        }
    
    def _generate_no_fall_analysis(self, video_info):
        """生成无跌倒事件的分析结果"""
        return {
            'summary': {
                'total_falls': 0,
                'risk_level': 'low',
                'processing_time': 0,
                'video_duration': video_info.get('duration', 0)
            },
            'fall_types': {'sustained': 0, 'sudden': 0, 'distribution': {}},
            'time_analysis': {'peak_hours': [], 'distribution': []},
            'confidence_analysis': {'average': 0, 'max': 0, 'min': 0, 'distribution': []},
            'chart_data': {'timeline': [], 'confidence_trend': [], 'risk_heatmap': []},
            'recommendations': [
                "✅ 演示模式：未检测到跌倒事件",
                "📊 活动状态正常",
                "🔍 建议定期检查以确保居家安全",
                "💡 演示模式提示：实际使用时将提供更精确的分析"
            ],
            'timeline': [],
            'demo_mode': True
        }
    
    def _generate_demo_recommendations(self, risk_level, total_falls, fall_types):
        """生成演示建议"""
        recommendations = ["🎯 演示模式分析建议："]
        
        if risk_level == 'low':
            recommendations.extend([
                "✅ 整体风险较低，状态良好",
                "🔍 建议保持定期观察",
                "💡 可考虑适当增加安全措施"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "⚠️ 检测到中等风险，需要关注",
                "👥 建议家属或护理人员定期检查",
                "🏥 可考虑咨询医疗专业人员"
            ])
        else:
            recommendations.extend([
                "🚨 检测到高风险情况，需要立即关注",
                "📞 建议立即联系家属或紧急联系人",
                "🏥 强烈建议寻求医疗帮助"
            ])
        
        recommendations.append("🔬 注意：这是演示模式结果，实际系统将提供更精确的分析")
        return recommendations
