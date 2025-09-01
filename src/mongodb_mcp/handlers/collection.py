"""Collection-level operations handler."""

from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import OperationFailure


class CollectionHandler:
    """Handles MongoDB collection-level operations."""
    
    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
    
    async def list_collections(self, database_name: str) -> List[Dict[str, Any]]:
        """列出指定数据库中的所有集合."""
        try:
            db = self.client[database_name]
            # 获取集合名称列表
            collection_names = await db.list_collection_names()
            
            # 构建集合信息列表
            collections = []
            for name in collection_names:
                collections.append({
                    'name': name,
                    'type': 'collection'
                })
            return collections
        except OperationFailure as e:
            raise RuntimeError(f"获取集合列表失败: {e}")
    
    async def describe_collection(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        """Get collection metadata, indexes, and sample schema."""
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            # Get indexes
            indexes = []
            async for index in collection.list_indexes():
                indexes.append(index)
            
            # Get collection stats
            stats = await db.command('collStats', collection_name)
            
            # Get sample documents to infer schema
            sample_docs = []
            async for doc in collection.aggregate([
                {'$sample': {'size': 5}},
                {'$project': {field: {'$type': f'${field}'} for field in ['_id']}}
            ]):
                # Extract field types from sample
                sample_docs.append(doc)
            
            return {
                'collection': collection_name,
                'database': database_name,
                'indexes': indexes,
                'stats': {
                    'count': stats.get('count', 0),
                    'size': stats.get('size', 0),
                    'storageSize': stats.get('storageSize', 0),
                    'avgObjSize': stats.get('avgObjSize', 0)
                },
                'sampleSchema': sample_docs
            }
        except OperationFailure as e:
            raise RuntimeError(f"Failed to describe collection: {e}")
    
    async def get_collection_stats(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        """Get collection performance statistics."""
        try:
            db = self.client[database_name]
            stats = await db.command('collStats', collection_name)
            
            return {
                'collection': collection_name,
                'database': database_name,
                'count': stats.get('count', 0),
                'size': stats.get('size', 0),
                'storageSize': stats.get('storageSize', 0),
                'avgObjSize': stats.get('avgObjSize', 0),
                'indexCount': stats.get('nindexes', 0),
                'indexSize': stats.get('totalIndexSize', 0)
            }
        except OperationFailure as e:
            raise RuntimeError(f"Failed to get collection stats: {e}")
    
    async def list_indexes(self, database_name: str, collection_name: str) -> List[Dict[str, Any]]:
        """List all indexes for a collection."""
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            indexes = []
            async for index in collection.list_indexes():
                indexes.append(index)
            return indexes
        except OperationFailure as e:
            raise RuntimeError(f"Failed to list indexes: {e}")