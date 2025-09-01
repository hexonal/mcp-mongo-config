"""MongoDB文档CRUD操作处理器."""

from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure
from bson import ObjectId

from ..security.validator import QueryValidator
from ..security.sanitizer import InputSanitizer


class DocumentHandler:
    """处理MongoDB文档操作的核心类."""
    
    def __init__(self, client: AsyncIOMotorClient, allow_dangerous: bool = False):
        """初始化文档处理器.
        
        Args:
            client: MongoDB异步客户端
            allow_dangerous: 是否允许危险的写操作
        """
        self.client = client
        self.allow_dangerous = allow_dangerous
    
    async def find_documents(
        self,
        database_name: str,
        collection_name: str,
        query: Dict[str, Any] = None,
        projection: Dict[str, Any] = None,
        sort: Dict[str, Any] = None,
        limit: int = 100,
        skip: int = 0
    ) -> Dict[str, Any]:
        """查找匹配查询条件的文档.
        
        Args:
            database_name: 数据库名称
            collection_name: 集合名称
            query: 查询条件字典
            projection: 投影字段（指定返回哪些字段）
            sort: 排序条件
            limit: 限制返回文档数量
            skip: 跳过的文档数量
            
        Returns:
            包含文档列表和元数据的字典
        """
        if query is None:
            query = {}
        
        try:
            # 验证和清理输入参数
            QueryValidator.validate_query(query, self.allow_dangerous)
            query = InputSanitizer.sanitize_query(query)
            
            db = self.client[database_name]
            collection = db[collection_name]
            
            # 构建查询游标并设置可选参数
            cursor = collection.find(query, projection)
            
            if sort:
                cursor = cursor.sort(list(sort.items()))
            
            if skip > 0:
                cursor = cursor.skip(skip)
            
            if limit > 0:
                cursor = cursor.limit(limit)
            
            # 执行查询并转换结果
            documents = []
            async for doc in cursor:
                # 将ObjectId转换为字符串以便JSON序列化
                if '_id' in doc and isinstance(doc['_id'], ObjectId):
                    doc['_id'] = str(doc['_id'])
                documents.append(doc)
            
            return {
                'documents': documents,
                'count': len(documents),
                'hasMore': len(documents) == limit,
                'query': query
            }
            
        except OperationFailure as e:
            raise RuntimeError(f"Query failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Find operation failed: {e}")
    
    async def find_one_document(
        self,
        database_name: str,
        collection_name: str,
        query: Dict[str, Any] = None,
        projection: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Find single document matching criteria."""
        if query is None:
            query = {}
        
        try:
            QueryValidator.validate_query(query, self.allow_dangerous)
            query = InputSanitizer.sanitize_query(query)
            
            db = self.client[database_name]
            collection = db[collection_name]
            
            doc = await collection.find_one(query, projection)
            
            if doc and '_id' in doc and isinstance(doc['_id'], ObjectId):
                doc['_id'] = str(doc['_id'])
            
            return doc
            
        except OperationFailure as e:
            raise RuntimeError(f"Find one failed: {e}")
    
    async def count_documents(
        self,
        database_name: str,
        collection_name: str,
        query: Dict[str, Any] = None
    ) -> int:
        """Count documents matching query."""
        if query is None:
            query = {}
        
        try:
            QueryValidator.validate_query(query, self.allow_dangerous)
            query = InputSanitizer.sanitize_query(query)
            
            db = self.client[database_name]
            collection = db[collection_name]
            
            return await collection.count_documents(query)
            
        except OperationFailure as e:
            raise RuntimeError(f"Count failed: {e}")
    
    async def insert_document(
        self,
        database_name: str,
        collection_name: str,
        document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Insert single document (dangerous mode required)."""
        if not self.allow_dangerous:
            raise PermissionError("Write operations require dangerous mode")
        
        try:
            document = InputSanitizer.sanitize_document(document)
            
            db = self.client[database_name]
            collection = db[collection_name]
            
            result = await collection.insert_one(document)
            
            return {
                'insertedId': str(result.inserted_id),
                'acknowledged': result.acknowledged
            }
            
        except OperationFailure as e:
            raise RuntimeError(f"Insert failed: {e}")
    
    async def update_document(
        self,
        database_name: str,
        collection_name: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False
    ) -> Dict[str, Any]:
        """Update documents matching query (dangerous mode required)."""
        if not self.allow_dangerous:
            raise PermissionError("Write operations require dangerous mode")
        
        try:
            QueryValidator.validate_query(query, self.allow_dangerous)
            query = InputSanitizer.sanitize_query(query)
            update = InputSanitizer.sanitize_document(update)
            
            db = self.client[database_name]
            collection = db[collection_name]
            
            result = await collection.update_many(query, update, upsert=upsert)
            
            return {
                'matchedCount': result.matched_count,
                'modifiedCount': result.modified_count,
                'upsertedId': str(result.upserted_id) if result.upserted_id else None,
                'acknowledged': result.acknowledged
            }
            
        except OperationFailure as e:
            raise RuntimeError(f"Update failed: {e}")
    
    async def delete_document(
        self,
        database_name: str,
        collection_name: str,
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Delete documents matching query (dangerous mode required)."""
        if not self.allow_dangerous:
            raise PermissionError("Write operations require dangerous mode")
        
        try:
            QueryValidator.validate_query(query, self.allow_dangerous)
            query = InputSanitizer.sanitize_query(query)
            
            db = self.client[database_name]
            collection = db[collection_name]
            
            result = await collection.delete_many(query)
            
            return {
                'deletedCount': result.deleted_count,
                'acknowledged': result.acknowledged
            }
            
        except OperationFailure as e:
            raise RuntimeError(f"Delete failed: {e}")