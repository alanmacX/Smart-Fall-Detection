"""
结果分析器 - 分析检测结果并生成可视化数据
"""

import json
import numpy as np
from datetime import datetime, timedelta
from collections import Counter

class ResultAnalyzer:
    def __init__(self):
        self.risk_levels = {
            'low': {'min_falls': 0, 'max_falls': 1, 'color': '#28a745'},
            'medium': {'min_falls': 2, 'max_falls': 4, 'color': '#ffc107'},
            'high': {'min_falls': 5, 'max_falls': float('inf'), 'color': '#dc3545'}
        }
    
    def analyze_detection_result(self, detection_result):
        """
        分析检测结果并生成统计数据
        
        Args:
            detection_result: 检测结果字典
            
        Returns:
            dict: 分析结果
        """
        fall_events = detection_result.get('fall_events', [])
        video_info = detection_result.get('video_info', {})
        
        if not fall_events:
            return self._generate_no_fall_analysis(video_info)
        
        # 基础统计
        total_falls = len(fall_events)
        fall_types = [event['type'] for event in fall_events]
        type_counts = Counter(fall_types)
        
        # 时间分析
        timestamps = [event['timestamp'] for event in fall_events]
        time_analysis = self._analyze_time_distribution(timestamps, video_info.get('duration', 0))
        
        # 置信度分析
        confidences = [event['confidence'] for event in fall_events]
        confidence_analysis = self._analyze_confidence(confidences)
        
        # 风险评估
        risk_level = self._assess_risk_level(total_falls, confidences)
        
        # 生成图表数据
        chart_data = self._generate_chart_data(fall_events, video_info)
        
        # 生成建议
        recommendations = self._generate_recommendations(risk_level, total_falls, fall_types)
        
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
                'distribution': dict(type_counts)
            },
            'time_analysis': time_analysis,
            'confidence_analysis': confidence_analysis,
            'chart_data': chart_data,
            'recommendations': recommendations,
            'timeline': self._generate_timeline(fall_events)
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
            'fall_types': {
                'sustained': 0,
                'sudden': 0,
                'distribution': {}
            },
            'time_analysis': {
                'peak_hours': [],
                'distribution': []
            },
            'confidence_analysis': {
                'average': 0,
                'max': 0,
                'min': 0,
                'distribution': []
            },
            'chart_data': {
                'timeline': [],
                'confidence_trend': [],
                'risk_heatmap': []
            },
            'recommendations': [
                "✅ 视频中未检测到跌倒事件",
                "📊 活动状态正常",
                "🔍 建议定期检查以确保居家安全"
            ],
            'timeline': []
        }
    
    def _analyze_time_distribution(self, timestamps, duration):
        """分析时间分布"""
        if not timestamps:
            return {'peak_hours': [], 'distribution': []}
        
        # 将时间戳转换为小时
        hours = [int((ts % 86400) // 3600) for ts in timestamps]
        hour_counts = Counter(hours)
        
        # 找出高峰时段
        peak_hours = [hour for hour, count in hour_counts.most_common(3)]
        
        # 生成24小时分布数据
        distribution = [{'hour': h, 'count': hour_counts.get(h, 0)} for h in range(24)]
        
        return {
            'peak_hours': peak_hours,
            'distribution': distribution,
            'total_duration_minutes': duration / 60
        }
    
    def _analyze_confidence(self, confidences):
        """分析置信度"""
        if not confidences:
            return {'average': 0, 'max': 0, 'min': 0, 'distribution': []}
        
        # 基础统计
        avg_conf = np.mean(confidences)
        max_conf = np.max(confidences)
        min_conf = np.min(confidences)
        
        # 置信度分布（分为5个区间）
        bins = np.linspace(0, 1, 6)
        hist, _ = np.histogram(confidences, bins=bins)
        
        distribution = []
        for i in range(len(bins)-1):
            distribution.append({
                'range': f"{bins[i]:.1f}-{bins[i+1]:.1f}",
                'count': int(hist[i])
            })
        
        return {
            'average': float(avg_conf),
            'max': float(max_conf),
            'min': float(min_conf),
            'distribution': distribution
        }
    
    def _assess_risk_level(self, total_falls, confidences):
        """评估风险等级"""
        if total_falls == 0:
            return 'low'
        
        # 基于跌倒次数
        for level, criteria in self.risk_levels.items():
            if criteria['min_falls'] <= total_falls <= criteria['max_falls']:
                base_level = level
                break
        else:
            base_level = 'high'
        
        # 基于置信度调整
        if confidences:
            avg_confidence = np.mean(confidences)
            if avg_confidence > 0.8 and base_level == 'low':
                return 'medium'
            elif avg_confidence > 0.9 and base_level == 'medium':
                return 'high'
        
        return base_level
    
    def _generate_chart_data(self, fall_events, video_info):
        """生成图表数据"""
        if not fall_events:
            return {'timeline': [], 'confidence_trend': [], 'risk_heatmap': []}
        
        # 时间轴数据
        timeline_data = []
        for event in fall_events:
            timeline_data.append({
                'timestamp': event['timestamp'],
                'frame': event['frame'],
                'confidence': event['confidence'],
                'type': event['type']
            })
        
        # 置信度趋势
        confidence_trend = []
        for i, event in enumerate(fall_events):
            confidence_trend.append({
                'x': i + 1,
                'y': event['confidence'],
                'type': event['type']
            })
        
        # 风险热力图（按时间分段）
        duration = video_info.get('duration', 0)
        if duration > 0:
            segment_count = max(1, min(20, int(duration // 30)))  # 每30秒一个分段，最多20个，至少1个
            segment_duration = duration / segment_count
            
            risk_heatmap = []
            for i in range(segment_count):
                start_time = i * segment_duration
                end_time = (i + 1) * segment_duration
                
                # 计算该时间段内的跌倒事件数
                events_in_segment = [
                    e for e in fall_events 
                    if start_time <= e['timestamp'] < end_time
                ]
                
                risk_level = len(events_in_segment)
                risk_heatmap.append({
                    'segment': i,
                    'start_time': start_time,
                    'end_time': end_time,
                    'risk_level': risk_level,
                    'events': len(events_in_segment)
                })
        else:
            risk_heatmap = []
        
        return {
            'timeline': timeline_data,
            'confidence_trend': confidence_trend,
            'risk_heatmap': risk_heatmap
        }
    
    def _generate_recommendations(self, risk_level, total_falls, fall_types):
        """生成关怀建议"""
        recommendations = []
        
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
                "🏥 可考虑咨询医疗专业人员",
                "🛡️ 建议加强居家安全措施"
            ])
        else:  # high
            recommendations.extend([
                "🚨 检测到高风险情况，需要立即关注",
                "📞 建议立即联系家属或紧急联系人",
                "🏥 强烈建议寻求医疗帮助",
                "👨‍⚕️ 考虑安排专业护理人员",
                "🛡️ 立即改善居住环境安全"
            ])
        
        # 基于跌倒类型的建议
        type_counter = Counter(fall_types)
        if type_counter.get('sudden', 0) > 0:
            recommendations.append("⚡ 检测到突发性跌倒，可能需要检查身体协调性")
        if type_counter.get('sustained', 0) > 0:
            recommendations.append("🕐 检测到持续性跌倒，可能需要评估起身能力")
        
        return recommendations
    
    def _generate_timeline(self, fall_events):
        """生成事件时间轴"""
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
                'description': f"第{i+1}次跌倒事件 ({event['type']}类型)"
            })
        
        return timeline
