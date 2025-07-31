/**
 * 智能跌倒检测系统 - 主要JavaScript文件
 * 处理文件上传、检测控制、进度监控等功能
 */

class FallDetectionApp {
    constructor() {
        this.currentTaskId = null;
        this.progressInterval = null;
        this.isProcessing = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadTaskHistory();
    }

    initializeElements() {
        // 文件相关元素
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('videoFile');
        this.videoPreview = document.getElementById('videoPreview');
        this.previewVideo = document.getElementById('previewVideo');
        this.videoFileName = document.getElementById('videoFileName');
        this.videoSize = document.getElementById('videoSize');
        
        // 参数控制元素
        this.detectionParams = document.getElementById('detectionParams');
        this.confidenceSlider = document.getElementById('confidenceSlider');
        this.confidenceValue = document.getElementById('confidenceValue');
        this.iouSlider = document.getElementById('iouSlider');
        this.iouValue = document.getElementById('iouValue');
        
        // 按钮元素
        this.uploadBtn = document.getElementById('uploadBtn');
        this.detectBtn = document.getElementById('detectBtn');
        this.viewDetailsBtn = document.getElementById('viewDetailsBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        
        // 状态显示元素
        this.statusSection = document.getElementById('statusSection');
        this.progressSection = document.getElementById('progressSection');
        this.progressBar = document.getElementById('progressBar');
        this.progressPercent = document.getElementById('progressPercent');
        this.progressMessage = document.getElementById('progressMessage');
        this.quickResults = document.getElementById('quickResults');
        
        // 结果显示元素
        this.fallCount = document.getElementById('fallCount');
        this.riskLevel = document.getElementById('riskLevel');
        this.confidence = document.getElementById('confidence');
        
        // 历史记录
        this.taskHistory = document.getElementById('taskHistory');
        
        // 模态框
        this.errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
        this.errorMessage = document.getElementById('errorMessage');
    }

    bindEvents() {
        // 文件上传事件
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        this.uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // 滑块事件
        this.confidenceSlider.addEventListener('input', this.updateConfidenceValue.bind(this));
        this.iouSlider.addEventListener('input', this.updateIouValue.bind(this));
        
        // 按钮事件
        this.uploadBtn.addEventListener('click', this.uploadVideo.bind(this));
        this.detectBtn.addEventListener('click', this.startDetection.bind(this));
        this.viewDetailsBtn.addEventListener('click', this.viewDetails.bind(this));
        this.downloadBtn.addEventListener('click', this.downloadResult.bind(this));
    }

    // 拖拽处理
    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }

    // 文件选择处理
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.handleFile(file);
        }
    }

    handleFile(file) {
        // 验证文件类型
        const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('请选择有效的视频文件格式（MP4、AVI、MOV）');
            return;
        }

        // 验证文件大小 (500MB)
        const maxSize = 500 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('文件大小超过500MB限制，请选择较小的文件');
            return;
        }

        // 显示视频预览
        this.showVideoPreview(file);
        
        // 显示检测参数
        this.detectionParams.style.display = 'block';
        
        // 启用上传按钮
        this.uploadBtn.disabled = false;
        
        // 存储文件
        this.selectedFile = file;
    }

    showVideoPreview(file) {
        // 更新文件信息
        this.videoFileName.textContent = file.name;
        this.videoSize.textContent = this.formatFileSize(file.size);
        
        // 创建视频预览
        const videoURL = URL.createObjectURL(file);
        this.previewVideo.src = videoURL;
        
        // 显示预览区域
        this.videoPreview.style.display = 'block';
        
        // 清理旧的URL
        this.previewVideo.addEventListener('loadeddata', () => {
            URL.revokeObjectURL(videoURL);
        });
    }

    // 滑块值更新
    updateConfidenceValue() {
        this.confidenceValue.textContent = this.confidenceSlider.value;
    }

    updateIouValue() {
        this.iouValue.textContent = this.iouSlider.value;
    }

    // 上传视频
    async uploadVideo() {
        if (!this.selectedFile) {
            this.showError('请先选择视频文件');
            return;
        }

        console.log('开始上传视频:', this.selectedFile.name);
        console.log('文件大小:', this.selectedFile.size);
        console.log('文件类型:', this.selectedFile.type);

        this.setLoading(this.uploadBtn, true, '上传中...');
        
        try {
            const formData = new FormData();
            formData.append('video', this.selectedFile);

            console.log('FormData创建完成，开始发送请求');

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            console.log('响应状态:', response.status, response.statusText);

            const result = await response.json();
            console.log('响应结果:', result);

            if (response.ok) {
                this.currentTaskId = result.task_id;
                this.showStatus(`视频上传成功: ${result.filename}`, 'success');
                
                // 显示检测按钮
                this.uploadBtn.style.display = 'none';
                this.detectBtn.style.display = 'block';
                this.detectBtn.disabled = false;
                
                console.log('上传成功，任务ID:', this.currentTaskId);
                
            } else {
                console.error('上传失败:', result.error);
                this.showError(result.error || '上传失败');
            }
        } catch (error) {
            console.error('上传过程中发生错误:', error);
            console.error('错误详情:', error.stack);
            this.showError('上传过程中发生错误: ' + error.message);
        } finally {
            this.setLoading(this.uploadBtn, false, '上传视频');
        }
    }

    // 开始检测
    async startDetection() {
        if (!this.currentTaskId) {
            this.showError('没有可用的任务ID');
            return;
        }

        this.isProcessing = true;
        this.setLoading(this.detectBtn, true, '检测中...');
        this.detectBtn.disabled = true;

        try {
            const params = {
                confidence: parseFloat(this.confidenceSlider.value),
                iou_threshold: parseFloat(this.iouSlider.value)
            };

            const response = await fetch(`/detect/${this.currentTaskId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });

            const result = await response.json();

            if (response.ok) {
                this.showStatus('检测任务已启动', 'info');
                this.startProgressMonitoring();
            } else {
                this.showError(result.error || '启动检测失败');
                this.isProcessing = false;
                this.setLoading(this.detectBtn, false, '开始检测');
            }
        } catch (error) {
            this.showError('启动检测过程中发生错误: ' + error.message);
            this.isProcessing = false;
            this.setLoading(this.detectBtn, false, '开始检测');
        }
    }

    // 监控检测进度
    startProgressMonitoring() {
        // 显示进度区域
        this.progressSection.style.display = 'block';
        this.statusSection.style.display = 'none';
        
        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${this.currentTaskId}`);
                const status = await response.json();

                if (response.ok) {
                    this.updateProgress(status);
                    
                    if (status.status === 'completed') {
                        this.onDetectionComplete(status);
                    } else if (status.status === 'error') {
                        this.onDetectionError(status);
                    }
                } else {
                    console.error('获取状态失败:', status);
                }
            } catch (error) {
                console.error('监控进度错误:', error);
            }
        }, 1000);
    }

    // 更新进度显示
    updateProgress(status) {
        const progress = Math.min(status.progress || 0, 100);
        this.progressBar.style.width = progress + '%';
        this.progressPercent.textContent = progress + '%';
        this.progressMessage.textContent = status.message || '处理中...';
        
        // 更新进度条颜色
        if (progress < 30) {
            this.progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-info';
        } else if (progress < 70) {
            this.progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-warning';
        } else {
            this.progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-success';
        }
    }

    // 检测完成处理
    onDetectionComplete(status) {
        clearInterval(this.progressInterval);
        this.isProcessing = false;
        
        // 隐藏进度条
        this.progressSection.style.display = 'none';
        
        // 显示结果
        this.showQuickResults(status.result);
        
        // 启用操作按钮
        this.viewDetailsBtn.disabled = false;
        this.downloadBtn.disabled = false;
        
        // 更新历史记录
        this.loadTaskHistory();
        
        this.showStatus('检测完成！', 'success');
    }

    // 检测错误处理
    onDetectionError(status) {
        clearInterval(this.progressInterval);
        this.isProcessing = false;
        
        this.progressSection.style.display = 'none';
        this.statusSection.style.display = 'block';
        
        this.showError('检测失败: ' + (status.message || '未知错误'));
        this.setLoading(this.detectBtn, false, '开始检测');
        this.detectBtn.disabled = false;
    }

    // 显示快速结果
    showQuickResults(result) {
        if (!result || !result.analysis) {
            return;
        }

        const analysis = result.analysis;
        
        // 更新统计数据
        this.fallCount.textContent = analysis.summary.total_falls || 0;
        this.riskLevel.textContent = this.getRiskLevelText(analysis.summary.risk_level);
        this.riskLevel.className = 'stat-number ' + this.getRiskLevelClass(analysis.summary.risk_level);
        
        // 计算平均置信度
        const avgConf = analysis.confidence_analysis?.average || 0;
        this.confidence.textContent = Math.round(avgConf * 100) + '%';
        
        // 显示结果区域
        this.quickResults.style.display = 'block';
    }

    // 查看详细结果
    viewDetails() {
        if (this.currentTaskId) {
            window.location.href = `/result/${this.currentTaskId}`;
        }
    }

    // 下载结果
    downloadResult() {
        if (this.currentTaskId) {
            window.location.href = `/download/${this.currentTaskId}`;
        }
    }

    // 加载历史任务
    async loadTaskHistory() {
        try {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();

            if (response.ok && tasks.length > 0) {
                this.renderTaskHistory(tasks);
            } else {
                this.taskHistory.innerHTML = `
                    <div class="text-center py-3">
                        <i class="fas fa-clock text-muted me-2"></i>
                        <span class="text-muted">暂无检测记录</span>
                    </div>
                `;
            }
        } catch (error) {
            console.error('加载历史记录失败:', error);
        }
    }

    // 渲染历史任务
    renderTaskHistory(tasks) {
        const historyHTML = tasks.slice(0, 5).map(task => {
            const uploadTime = new Date(task.upload_time).toLocaleString('zh-CN');
            const statusClass = `status-${task.status}`;
            const statusText = this.getStatusText(task.status);
            
            return `
                <div class="task-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">
                                <i class="fas fa-video me-2 text-muted"></i>
                                ${task.filename}
                            </h6>
                            <small class="text-muted">
                                <i class="fas fa-clock me-1"></i>
                                ${uploadTime}
                            </small>
                        </div>
                        <div class="text-end">
                            <span class="task-status ${statusClass}">${statusText}</span>
                            ${task.status === 'completed' ? 
                                `<div class="mt-1">
                                    <button class="btn btn-sm btn-outline-primary" onclick="app.viewTaskResult('${task.id}')">
                                        <i class="fas fa-eye me-1"></i>查看
                                    </button>
                                </div>` : 
                                `<div class="mt-1">
                                    <small class="text-muted">${task.progress}%</small>
                                </div>`
                            }
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        this.taskHistory.innerHTML = historyHTML;
    }

    // 查看任务结果
    viewTaskResult(taskId) {
        window.location.href = `/result/${taskId}`;
    }

    // 工具方法
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getRiskLevelText(level) {
        const levels = {
            'low': '低风险',
            'medium': '中风险',
            'high': '高风险'
        };
        return levels[level] || '未知';
    }

    getRiskLevelClass(level) {
        const classes = {
            'low': 'text-success',
            'medium': 'text-warning',
            'high': 'text-danger'
        };
        return classes[level] || 'text-muted';
    }

    getStatusText(status) {
        const statusTexts = {
            'pending': '等待中',
            'processing': '处理中',
            'completed': '已完成',
            'error': '失败'
        };
        return statusTexts[status] || status;
    }

    setLoading(button, loading, text = '') {
        if (loading) {
            button.innerHTML = `
                <span class="loading-spinner me-2"></span>
                ${text}
            `;
            button.disabled = true;
        } else {
            button.innerHTML = text;
            button.disabled = false;
        }
    }

    showStatus(message, type = 'info') {
        const icons = {
            'info': 'fas fa-info-circle',
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle',
            'error': 'fas fa-times-circle'
        };

        const colors = {
            'info': 'text-info',
            'success': 'text-success',
            'warning': 'text-warning',
            'error': 'text-danger'
        };

        this.statusSection.innerHTML = `
            <div class="text-center py-4">
                <i class="${icons[type]} fa-2x ${colors[type]} mb-3"></i>
                <p class="${colors[type]}">${message}</p>
            </div>
        `;
        this.statusSection.style.display = 'block';
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorModal.show();
    }
}

// 性能配置相关功能
function updatePerformanceConfig() {
    const config = {
        use_gpu: document.getElementById('useGpu').checked,
        skip_frames: parseInt(document.getElementById('skipFrames').value),
        detection_conf: parseFloat(document.getElementById('detectionConf').value),
        iou_threshold: parseFloat(document.getElementById('iouThreshold').value)
    };
    
    fetch('/api/performance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        const statusEl = document.getElementById('perfStatus');
        if (data.success) {
            statusEl.innerHTML = '<i class="fas fa-check text-success"></i> 配置已更新';
            setTimeout(() => {
                statusEl.innerHTML = '';
            }, 3000);
        } else {
            statusEl.innerHTML = '<i class="fas fa-times text-danger"></i> 更新失败';
        }
    })
    .catch(error => {
        console.error('性能配置更新失败:', error);
        document.getElementById('perfStatus').innerHTML = '<i class="fas fa-times text-danger"></i> 网络错误';
    });
}

// 加载性能配置
function loadPerformanceConfig() {
    fetch('/api/performance')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const config = data.config;
            document.getElementById('useGpu').checked = config.use_gpu;
            document.getElementById('skipFrames').value = config.skip_frames;
            document.getElementById('detectionConf').value = config.detection_conf;
            document.getElementById('iouThreshold').value = config.iou_threshold;
            
            // 更新显示值
            document.getElementById('confValue').textContent = config.detection_conf;
            document.getElementById('iouValue').textContent = config.iou_threshold;
        }
    })
    .catch(error => {
        console.error('加载性能配置失败:', error);
    });
}

// 初始化应用
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new FallDetectionApp();
    
    // 滑块值更新
    const detectionConf = document.getElementById('detectionConf');
    const confValue = document.getElementById('confValue');
    if (detectionConf && confValue) {
        detectionConf.addEventListener('input', function() {
            confValue.textContent = this.value;
        });
    }
    
    const iouThreshold = document.getElementById('iouThreshold');
    const iouValue = document.getElementById('iouValue');
    if (iouThreshold && iouValue) {
        iouThreshold.addEventListener('input', function() {
            iouValue.textContent = this.value;
        });
    }
    
    // 加载初始性能配置
    loadPerformanceConfig();
    
    // 定期刷新历史记录
    setInterval(() => {
        if (!app.isProcessing) {
            app.loadTaskHistory();
        }
    }, 30000); // 每30秒刷新一次
});
