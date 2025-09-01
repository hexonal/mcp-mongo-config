"""Aggregation pipeline operations handler."""

from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure
from bson import ObjectId

from ..security.validator import AggregationValidator
from ..security.sanitizer import InputSanitizer


class AggregationHandler:
    """Handles MongoDB aggregation operations."""
    
    def __init__(self, client: AsyncIOMotorClient, allow_dangerous: bool = False):
        self.client = client
        self.allow_dangerous = allow_dangerous
    
    async def aggregate_pipeline(
        self,
        database_name: str,
        collection_name: str,
        pipeline: List[Dict[str, Any]],
        limit: int = 100,
        max_stages: int = 20
    ) -> Dict[str, Any]:
        """Execute MongoDB aggregation pipeline."""
        try:
            # Validate pipeline
            AggregationValidator.validate_pipeline(
                pipeline, self.allow_dangerous, max_stages
            )
            
            # Sanitize pipeline stages
            sanitized_pipeline = []
            for stage in pipeline:
                sanitized_stage = InputSanitizer.sanitize_query(stage)
                sanitized_pipeline.append(sanitized_stage)
            
            # Add automatic limit if not present
            has_limit = any('$limit' in stage for stage in sanitized_pipeline)
            if not has_limit and limit > 0:
                sanitized_pipeline.append({'$limit': limit})
            
            db = self.client[database_name]
            collection = db[collection_name]
            
            # Execute aggregation
            results = []
            async for doc in collection.aggregate(sanitized_pipeline):
                # Convert ObjectId to string for JSON serialization
                if '_id' in doc and isinstance(doc['_id'], ObjectId):
                    doc['_id'] = str(doc['_id'])
                results.append(doc)
            
            return {
                'results': results,
                'count': len(results),
                'pipeline': sanitized_pipeline,
                'hasMore': len(results) == limit
            }
            
        except OperationFailure as e:
            raise RuntimeError(f"Aggregation failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Pipeline execution failed: {e}")
    
    async def explain_aggregation(
        self,
        database_name: str,
        collection_name: str,
        pipeline: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get execution plan for aggregation pipeline."""
        try:
            AggregationValidator.validate_pipeline(
                pipeline, self.allow_dangerous
            )
            
            db = self.client[database_name]
            collection = db[collection_name]
            
            # Get execution stats
            explain_pipeline = pipeline + [{'$explain': {'verbosity': 'executionStats'}}]
            
            result = await collection.aggregate(explain_pipeline).to_list(length=1)
            
            return {
                'executionPlan': result[0] if result else {},
                'pipeline': pipeline
            }
            
        except OperationFailure as e:
            raise RuntimeError(f"Explain failed: {e}")
    
    async def create_index(
        self,
        database_name: str,
        collection_name: str,
        keys: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Create index on collection."""
        if not self.allow_dangerous:
            raise PermissionError("Index creation requires dangerous mode")
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            index_name = await collection.create_index(list(keys.items()), **kwargs)
            
            return {
                'indexName': index_name,
                'keys': keys,
                'options': kwargs
            }
            
        except OperationFailure as e:
            raise RuntimeError(f"Index creation failed: {e}")