"""Code execution tools for the software engineering task."""

import subprocess
import tempfile
import os
import sys
from typing import Dict, Any, Optional
import ast


class CodeRunner:
    """Simple code execution tool for Python code."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.execution_history: list = []
    
    async def run(self, code: str, filename: Optional[str] = None) -> Dict[str, Any]:
        result = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "return_code": None,
            "filename": filename or "temp_script.py"
        }
        
        syntax_check = self._validate_syntax(code)
        if not syntax_check["valid"]:
            result["stderr"] = f"Syntax Error: {syntax_check['error']}"
            return result
        
        security_check = self._security_check(code)
        if not security_check["safe"]:
            result["stderr"] = f"Security check failed: {security_check['reason']}"
            return result
        
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                temp_file = f.name
                f.write(code)
            
            proc = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            result["return_code"] = proc.returncode
            result["stdout"] = proc.stdout
            result["stderr"] = proc.stderr
            result["success"] = (proc.returncode == 0)
            
        except subprocess.TimeoutExpired:
            result["stderr"] = f"Execution timed out after {self.timeout} seconds"
        except Exception as e:
            result["stderr"] = f"Execution error: {str(e)}"
        finally:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
        
        return result
    
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        try:
            ast.parse(code)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {"valid": False, "error": f"Line {e.lineno}: {e.msg}"}
    
    def _security_check(self, code: str) -> Dict[str, Any]:
        dangerous_patterns = [
            "os.system", "subprocess.call", "subprocess.Popen",
            "eval(", "exec(", "__import__", "socket.", "urllib.request"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                return {"safe": False, "reason": f"Potentially dangerous pattern: {pattern}"}
        
        return {"safe": True, "reason": None}