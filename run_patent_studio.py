"""
启动专利智能工作室 Patent Studio

使用方法:
    python run_patent_studio.py

或者直接运行:
    streamlit run ui/patent_studio.py
"""

import os
import sys
import subprocess
import io

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def check_dependencies():
    """检查依赖"""
    missing = []
    
    try:
        import streamlit
        print("✓ Streamlit 已安装")
    except ImportError:
        missing.append("streamlit")
    
    try:
        import openai
        print("✓ OpenAI SDK 已安装")
    except ImportError:
        missing.append("openai")
    
    try:
        import pydantic
        print("✓ Pydantic 已安装")
    except ImportError:
        missing.append("pydantic")
    
    # 可选依赖
    try:
        import docx
        print("✓ python-docx 已安装（支持 Word 文件）")
    except ImportError:
        print("⚠ python-docx 未安装（无法读取 Word 文件）")
        print("  安装命令: pip install python-docx")
    
    try:
        import PyPDF2
        print("✓ PyPDF2 已安装（支持 PDF 文件）")
    except ImportError:
        print("⚠ PyPDF2 未安装（无法读取 PDF 文件）")
        print("  安装命令: pip install PyPDF2")
    
    if missing:
        print(f"\n❌ 缺少必要依赖: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False
    
    return True


def main():
    """启动专利智能工作室"""
    print("=" * 60)
    print("        ⚡ 专利智能工作室 Patent Studio")
    print("=" * 60)
    print()
    
    # 检查依赖
    print("检查依赖...")
    if not check_dependencies():
        return
    
    print()
    print("AI 模型: DeepSeek Chat")
    print("API 状态: ✓ 已配置")
    print()
    
    # 获取脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(script_dir, "ui", "patent_studio.py")
    
    print(f"启动界面: {ui_path}")
    print()
    print("正在启动 Streamlit 服务器...")
    print("请在浏览器中访问显示的地址（通常是 http://localhost:8501）")
    print()
    print("-" * 60)
    
    # 启动 Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            ui_path,
            "--server.headless", "true",
            "--server.address", "0.0.0.0",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false",
            "--theme.primaryColor", "#667eea",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f8fafc",
        ])
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n启动失败: {e}")
        print("\n请尝试手动运行:")
        print(f"  streamlit run {ui_path}")


if __name__ == "__main__":
    main()
