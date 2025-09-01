"""Database-level operations handler."""

from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure


class DatabaseHandler:
    """Handles MongoDB database-level operations."""
    
    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
    
    async def list_databases(self) -> List[Dict[str, Any]]:
        """列出所有可用的数据库."""
        try:
            # 使用admin.command方式获取数据库列表
            admin_db = self.client.admin
            result = await admin_db.command("listDatabases")
            return result.get('databases', [])
        except OperationFailure as e:
            raise RuntimeError(f"获取数据库列表失败: {e}")
    
    async def get_database_stats(self, database_name: str) -> Dict[str, Any]:
        """获取数据库详细统计信息."""
        try:
            db = self.client[database_name]
            stats = await db.command('dbStats')
            return {
                'database': database_name,
                'collections': stats.get('collections', 0),  # 集合数量
                'objects': stats.get('objects', 0),  # 文档数量
                'avgObjSize': stats.get('avgObjSize', 0),  # 平均文档大小
                'dataSize': stats.get('dataSize', 0),  # 数据大小
                'storageSize': stats.get('storageSize', 0),  # 存储大小
                'indexes': stats.get('indexes', 0),  # 索引数量
                'indexSize': stats.get('indexSize', 0)  # 索引大小
            }
        except OperationFailure as e:
            raise RuntimeError(f"获取数据库统计失败: {e}")
    
    async def database_exists(self, database_name: str) -> bool:
        """检查数据库是否存在."""
        try:
            databases = await self.list_databases()
            return any(db['name'] == database_name for db in databases)
        except Exception:
            return False