"""
Python 代码执行工具 (封装 REPL)

使用 langchain_experimental 的 Python REPL 安全执行候选人代码。
注意：此工具应在沙箱环境中使用，避免执行恶意代码。
"""
import sys
import traceback
from io import StringIO
from typing import Dict, Any

from langchain_core.tools import tool
from langchain_experimental.tools import PythonREPLTool


@tool
def execute_python_code(code: str) -> Dict[str, Any]:
    """
    执行候选人提交的 Python 代码并返回运行结果。
    用于验证算法题、代码片段是否正确。

    Args:
        code: 需要执行的 Python 代码字符串

    Returns:
        包含 stdout、stderr 和是否成功的字典
    """
    # 捕获 stdout
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_stdout = StringIO()
    redirected_stderr = StringIO()
    sys.stdout = redirected_stdout
    sys.stderr = redirected_stderr

    result = {"success": False, "stdout": "", "stderr": "", "error": ""}

    try:
        # 使用 exec 执行代码（限制内置函数，避免危险操作）
        restricted_builtins = {
            'print': print,
            'len': len,
            'range': range,
            'int': int,
            'float': float,
            'str': str,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'bool': bool,
            'True': True,
            'False': False,
            'None': None,
            'sorted': sorted,
            'reversed': reversed,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'any': any,
            'all': all,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'isinstance': isinstance,
            'type': type,
            'hasattr': hasattr,
            'getattr': getattr,
            'setattr': setattr,
            '__import__': __import__,
        }

        exec_globals = {"__builtins__": restricted_builtins}
        exec(code, exec_globals)
        result["success"] = True
    except Exception as e:
        result["error"] = str(e)
        result["stderr"] = traceback.format_exc()
    finally:
        result["stdout"] = redirected_stdout.getvalue()
        result["stderr"] += redirected_stderr.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return result


# 备选：使用 langchain_experimental 的 PythonREPLTool
# 更安全但需要额外依赖
def get_python_repl_tool() -> PythonREPLTool:
    """获取 PythonREPLTool 实例（依赖 langchain-experimental）"""
    return PythonREPLTool()
