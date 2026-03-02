import subprocess
import logging

class CommandRunner:
    """命令执行工具类"""
    
    @staticmethod
    def run_command(cmd, timeout=30):
        """执行系统命令并返回结果"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timeout after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    @staticmethod
    def safe_run(cmd, default=None):
        """安全执行命令，出错时返回默认值"""
        try:
            result = CommandRunner.run_command(cmd)
            return result['stdout'] if result['success'] else default
        except:
            return default
