"""MongoDB Model Context Protocol server."""

__version__ = "0.1.0"
__author__ = "MongoDB MCP Contributors"

# 核心组件可以独立导入和测试
from .config import get_config, MongoDBConfig
from .connection import MongoDBConnection

__all__ = ["get_config", "MongoDBConfig", "MongoDBConnection"]