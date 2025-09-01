"""MongoDB连接管理模块."""

import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from .config import MongoDBConfig


class MongoDBConnection:
    """管理MongoDB连接生命周期."""
    
    def __init__(self, config: MongoDBConfig):
        self.config = config
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """建立MongoDB连接."""
        try:
            self._client = AsyncIOMotorClient(
                self.config.connection_uri,
                serverSelectionTimeoutMS=self.config.mongodb_timeout * 1000
            )
            
            # 测试连接
            await self._client.admin.command('ping')
            
            self._database = self._client[self.config.mongodb_database]
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionError(f"连接MongoDB失败: {e}")
    
    async def disconnect(self) -> None:
        """关闭MongoDB连接."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
    
    @property
    def client(self) -> AsyncIOMotorClient:
        """获取MongoDB客户端实例."""
        if not self._client:
            raise RuntimeError("未连接到MongoDB")
        return self._client
    
    @property
    def database(self) -> AsyncIOMotorDatabase:
        """获取默认数据库实例."""
        if not self._database:
            raise RuntimeError("未连接到MongoDB")
        return self._database
    
    def get_database(self, name: str) -> AsyncIOMotorDatabase:
        """获取指定数据库实例."""
        if not self._client:
            raise RuntimeError("未连接到MongoDB")
        return self._client[name]