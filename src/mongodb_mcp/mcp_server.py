#!/usr/bin/env python3
"""标准MCP协议stdio服务器实现."""

import json
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加路径支持
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mongodb_mcp.config import get_config
from mongodb_mcp.connection import MongoDBConnection
from mongodb_mcp.handlers import DatabaseHandler, CollectionHandler, DocumentHandler, AggregationHandler

# 配置日志输出到stderr，避免干扰stdio通信
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class MCPServer:
    """标准MCP协议服务器实现."""
    
    def __init__(self):
        """初始化MCP服务器."""
        self.config = get_config()
        self.connection = MongoDBConnection(self.config)
        self.handlers = {}
        self.initialized = False
        
        logger.info("MongoDB MCP服务器初始化中...")
        logger.info(f"连接配置: {self.config.mongodb_host}:{self.config.mongodb_port}")
        logger.info(f"目标数据库: {self.config.mongodb_database}")
        logger.info(f"集群模式: {self.config.is_cluster_mode}")
    
    async def setup_handlers(self):
        """设置MongoDB处理器."""
        try:
            await self.connection.connect()
            logger.info("✅ MongoDB连接建立成功")
            
            self.handlers = {
                'database': DatabaseHandler(self.connection.client),
                'collection': CollectionHandler(self.connection.client),
                'document': DocumentHandler(self.connection.client, self.config.mongodb_allow_dangerous),
                'aggregation': AggregationHandler(self.connection.client, self.config.mongodb_allow_dangerous)
            }
            
            self.initialized = True
            logger.info("✅ 所有处理器初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 处理器初始化失败: {e}")
            return False
    
    def send_response(self, id: Optional[int], result: Any):
        """发送MCP响应到stdout."""
        response = {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }
        json.dump(response, sys.stdout, ensure_ascii=False)
        sys.stdout.write('\n')
        sys.stdout.flush()
        logger.debug(f"发送响应: {response}")
    
    def send_error(self, id: Optional[int], code: int, message: str):
        """发送错误响应到stdout."""
        error_response = {
            "jsonrpc": "2.0",
            "id": id,
            "error": {
                "code": code,
                "message": message
            }
        }
        json.dump(error_response, sys.stdout, ensure_ascii=False)
        sys.stdout.write('\n')
        sys.stdout.flush()
        logger.error(f"发送错误: {message}")
    
    async def handle_initialize(self, id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP初始化请求."""
        logger.info("处理初始化请求...")
        
        if not self.initialized:
            success = await self.setup_handlers()
            if not success:
                raise RuntimeError("服务器初始化失败")
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "mongodb-mcp",
                "version": "0.1.0",
                "description": "MongoDB模型上下文协议服务器"
            }
        }
    
    async def handle_tools_list(self, id: int) -> Dict[str, Any]:
        """处理工具列表请求."""
        logger.info("处理工具列表请求...")
        
        tools = [
            {
                "name": "list_databases",
                "description": "列出所有可用的MongoDB数据库",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "list_collections", 
                "description": "列出数据库中的集合",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string", "description": "数据库名称"}
                    },
                    "required": ["database"]
                }
            },
            {
                "name": "find_documents",
                "description": "查询匹配条件的文档", 
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string", "description": "数据库名称"},
                        "collection": {"type": "string", "description": "集合名称"},
                        "query": {"type": "object", "description": "查询条件"},
                        "limit": {"type": "integer", "description": "限制结果数量", "default": 100}
                    },
                    "required": ["database", "collection"]
                }
            },
            {
                "name": "count_documents",
                "description": "统计匹配条件的文档数量",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "database": {"type": "string", "description": "数据库名称"},
                        "collection": {"type": "string", "description": "集合名称"},
                        "query": {"type": "object", "description": "查询条件"}
                    },
                    "required": ["database", "collection"]
                }
            },
            {
                "name": "aggregate_pipeline",
                "description": "执行MongoDB聚合管道",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string", "description": "数据库名称"},
                        "collection": {"type": "string", "description": "集合名称"},
                        "pipeline": {"type": "array", "description": "聚合管道阶段"},
                        "limit": {"type": "integer", "description": "限制结果数量", "default": 100}
                    },
                    "required": ["database", "collection", "pipeline"]
                }
            }
        ]
        
        return {"tools": tools}
    
    async def handle_tool_call(self, id: int, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用请求."""
        logger.info(f"调用工具: {name}")
        
        if not self.initialized:
            raise RuntimeError("服务器未初始化")
        
        try:
            if name == "list_databases":
                result = await self.handlers['database'].list_databases()
                
            elif name == "list_collections":
                database = arguments.get('database')
                result = await self.handlers['collection'].list_collections(database)
                
            elif name == "find_documents":
                database = arguments.get('database')
                collection = arguments.get('collection')
                query = arguments.get('query', {})
                limit = arguments.get('limit', 100)
                
                result = await self.handlers['document'].find_documents(
                    database, collection, query, limit=limit
                )
                
            elif name == "count_documents":
                database = arguments.get('database')
                collection = arguments.get('collection')
                query = arguments.get('query', {})
                
                result = await self.handlers['document'].count_documents(
                    database, collection, query
                )
                
            elif name == "aggregate_pipeline":
                database = arguments.get('database')
                collection = arguments.get('collection')
                pipeline = arguments.get('pipeline', [])
                limit = arguments.get('limit', 100)
                
                result = await self.handlers['aggregation'].aggregate_pipeline(
                    database, collection, pipeline, limit
                )
                
            else:
                raise ValueError(f"未知工具: {name}")
            
            logger.info(f"✅ 工具 {name} 执行成功")
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}
            
        except Exception as e:
            logger.error(f"❌ 工具 {name} 执行失败: {e}")
            raise
    
    async def run(self):
        """运行MCP服务器主循环."""
        logger.info("🚀 MongoDB MCP服务器启动")
        logger.info("📡 等待stdio输入...")
        
        try:
            while True:
                # 从stdin读取请求
                line = sys.stdin.readline()
                if not line:
                    logger.info("📡 收到EOF，服务器关闭")
                    break
                
                try:
                    request = json.loads(line.strip())
                    logger.debug(f"收到请求: {request}")
                    
                    method = request.get('method')
                    params = request.get('params', {})
                    req_id = request.get('id')
                    
                    if method == 'initialize':
                        result = await self.handle_initialize(req_id, params)
                        self.send_response(req_id, result)
                        
                    elif method == 'tools/list':
                        result = await self.handle_tools_list(req_id)
                        self.send_response(req_id, result)
                        
                    elif method == 'tools/call':
                        tool_name = params.get('name')
                        tool_args = params.get('arguments', {})
                        result = await self.handle_tool_call(req_id, tool_name, tool_args)
                        self.send_response(req_id, result)
                        
                    else:
                        self.send_error(req_id, -32601, f"未知方法: {method}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {e}")
                    self.send_error(None, -32700, "JSON解析错误")
                    
                except Exception as e:
                    logger.error(f"请求处理错误: {e}")
                    self.send_error(req_id, -32603, f"内部错误: {e}")
                    
        except KeyboardInterrupt:
            logger.info("🛑 收到中断信号，服务器关闭")
        finally:
            if self.connection:
                await self.connection.disconnect()
            logger.info("🔚 服务器已关闭")


async def main():
    """主函数."""
    server = MCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())