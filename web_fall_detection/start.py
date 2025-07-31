#!/usr/bin/env python3
"""
智能跌倒检测Web系统 - 快速启动脚本
检查环境依赖并启动Web服务
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"   当前版本: Python {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
        return True

def check_models():
    """检查模型文件是否存在"""
    model_paths = [
        "../models/best.pt",
        "../models/yolov8n-pose.pt", 
        "../models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    ]
    
    missing_models = []
    for model_path in model_paths:
        if not os.path.exists(model_path):
            missing_models.append(model_path)
        else:
            print(f"✅ 找到模型文件: {model_path}")
    
    if missing_models:
        print("⚠️ 以下模型文件缺失:")
        for model in missing_models:
            print(f"   - {model}")
        print("   系统将在演示模式下运行")
        return False
    else:
        print("✅ 所有模型文件就绪")
        return True

def install_requirements():
    """安装依赖包"""
    print("🔄 检查并安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False

def create_directories():
    """创建必要的目录"""
    directories = [
        "static/uploads",
        "static/outputs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 创建目录: {directory}")

def start_server():
    """启动Web服务器"""
    print("\n" + "="*60)
    print("🚀 启动智能跌倒检测Web系统")
    print("="*60)
    print("📍 主页地址: http://localhost:5000")
    print("� 测试页面: http://localhost:5000/test")
    print("�📖 使用说明:")
    print("   1. 上传视频文件（支持MP4、AVI、MOV格式）")
    print("   2. 调整检测参数")
    print("   3. 开始智能检测")
    print("   4. 查看分析结果")
    print("="*60)
    print("💡 提示: 按Ctrl+C停止服务")
    print("💡 调试: 如遇上传问题，请访问测试页面")
    print("="*60)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🔧 智能跌倒检测Web系统 - 环境检查")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 创建必要目录
    create_directories()
    
    # 检查依赖
    print("\n🔍 检查系统依赖...")
    try:
        import flask
        print("✅ Flask已安装")
    except ImportError:
        print("📦 正在安装依赖...")
        if not install_requirements():
            sys.exit(1)
    
    # 检查模型文件
    print("\n🔍 检查模型文件...")
    models_ready = check_models()
    
    if not models_ready:
        print("\n⚠️ 警告: 部分模型文件缺失")
        print("   系统将以演示模式运行，部分功能可能受限")
        response = input("   是否继续启动? (y/N): ")
        if response.lower() != 'y':
            print("👋 启动已取消")
            sys.exit(0)
    
    print("\n✅ 环境检查完成，准备启动服务...")
    input("按回车键继续...")
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
