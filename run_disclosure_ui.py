"""
启动专利交底书提交系统

使用方法:
    python run_disclosure_ui.py
    
或者直接运行:
    streamlit run ui/disclosure_ui.py
"""

import os
import sys
import subprocess


def main():
    """启动交底书提交系统"""
    print("=" * 60)
    print("        专利交底书提交系统")
    print("=" * 60)
    print()
    
    # 检查 API 密钥
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"✓ GOOGLE_API_KEY 已配置: {api_key[:10]}...")
    else:
        print("⚠ GOOGLE_API_KEY 未配置")
        print("  请设置环境变量：")
        print("  Windows: set GOOGLE_API_KEY=your_api_key")
        print("  Linux/Mac: export GOOGLE_API_KEY=your_api_key")
        print()
    
    # 获取脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(script_dir, "ui", "disclosure_ui.py")
    
    print(f"启动界面: {ui_path}")
    print()
    print("正在启动 Streamlit 服务器...")
    print("请在浏览器中访问显示的地址")
    print()
    print("-" * 60)
    
    # 启动 Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            ui_path,
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n启动失败: {e}")
        print("\n请尝试手动运行:")
        print(f"  streamlit run {ui_path}")


if __name__ == "__main__":
    main()
