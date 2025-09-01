#!/usr/bin/env python3
"""MongoDB MCP服务器主入口，支持python -m mongodb_mcp启动."""

import asyncio
import sys
from pathlib import Path

# 确保能导入本模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from mongodb_mcp.simple_server import main

if __name__ == "__main__":
    # 使用独立服务器实现
    try:
        import subprocess
        import os
        
        # 直接运行独立服务器
        standalone_server = Path(__file__).parent.parent.parent / "standalone_mcp_server.py"
        
        # 传递环境变量
        env = os.environ.copy()
        
        # 启动独立服务器
        process = subprocess.run(
            [sys.executable, str(standalone_server)],
            env=env
        )
        
        sys.exit(process.returncode)
        
    except Exception as e:
        print(f"启动失败: {e}", file=sys.stderr)
        sys.exit(1)