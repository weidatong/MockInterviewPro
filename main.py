"""
MockInterview Pro - CLI 主入口

用法：
    python main.py

按照提示输入 JD（岗位描述），即可开始多轮模拟面试。
输入 'quit' 退出面试。
"""
from app.graph import run_cli

if __name__ == '__main__':
    run_cli()
