"""Query and operation validation for MongoDB MCP."""

from typing import Dict, List, Any, Set
from pydantic import BaseModel, Field, validator


class QueryValidator:
    """Validates MongoDB queries for security."""
    
    # Allowed query operators in safe mode
    SAFE_QUERY_OPERATORS: Set[str] = {
        "$eq", "$ne", "$gt", "$gte", "$lt", "$lte", 
        "$in", "$nin", "$exists", "$type", "$regex",
        "$and", "$or", "$not", "$nor", "$size",
        "$elemMatch", "$all"
    }
    
    # Dangerous operators that require explicit permission
    DANGEROUS_OPERATORS: Set[str] = {
        "$where", "$expr", "$jsonSchema", "$text"
    }
    
    @classmethod
    def validate_query(cls, query: Dict[str, Any], allow_dangerous: bool = False) -> None:
        """Validate MongoDB query structure."""
        cls._validate_dict(query, allow_dangerous)
    
    @classmethod
    def _validate_dict(cls, obj: Dict[str, Any], allow_dangerous: bool) -> None:
        """Recursively validate dictionary structure."""
        for key, value in obj.items():
            if key.startswith("$"):
                if key in cls.DANGEROUS_OPERATORS and not allow_dangerous:
                    raise ValueError(f"Dangerous operator '{key}' not allowed in safe mode")
                elif key not in cls.SAFE_QUERY_OPERATORS and key not in cls.DANGEROUS_OPERATORS:
                    raise ValueError(f"Unknown or forbidden operator: {key}")
            
            if isinstance(value, dict):
                cls._validate_dict(value, allow_dangerous)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        cls._validate_dict(item, allow_dangerous)


class AggregationValidator:
    """Validates MongoDB aggregation pipelines."""
    
    # Safe aggregation stages
    SAFE_STAGES: Set[str] = {
        "$match", "$project", "$sort", "$limit", "$skip", 
        "$group", "$unwind", "$lookup", "$addFields",
        "$count", "$facet", "$bucket", "$sample"
    }
    
    # Dangerous stages requiring special permission
    DANGEROUS_STAGES: Set[str] = {
        "$out", "$merge", "$geoNear", "$graphLookup", 
        "$function", "$accumulator", "$expr"
    }
    
    @classmethod
    def validate_pipeline(
        cls, 
        pipeline: List[Dict[str, Any]], 
        allow_dangerous: bool = False,
        max_stages: int = 20
    ) -> None:
        """Validate aggregation pipeline."""
        if len(pipeline) > max_stages:
            raise ValueError(f"Pipeline exceeds maximum {max_stages} stages")
        
        for i, stage in enumerate(pipeline):
            if not isinstance(stage, dict):
                raise ValueError(f"Stage {i} must be a dictionary")
            
            if len(stage) != 1:
                raise ValueError(f"Stage {i} must contain exactly one operation")
            
            stage_name = next(iter(stage.keys()))
            
            if stage_name in cls.DANGEROUS_STAGES and not allow_dangerous:
                raise ValueError(f"Dangerous stage '{stage_name}' not allowed in safe mode")
            elif stage_name not in cls.SAFE_STAGES and stage_name not in cls.DANGEROUS_STAGES:
                raise ValueError(f"Unknown or forbidden stage: {stage_name}")


class DocumentValidator(BaseModel):
    """Validates document operations."""
    
    database: str = Field(..., min_length=1, max_length=64)
    collection: str = Field(..., min_length=1, max_length=64)
    
    @validator('database', 'collection')
    def validate_name(cls, v):
        """Validate database and collection names."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Names must be alphanumeric with underscores/hyphens")
        return v