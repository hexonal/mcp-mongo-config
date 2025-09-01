"""Input sanitization for MongoDB MCP."""

from typing import Any, Dict, List, Union
import re


class InputSanitizer:
    """Sanitizes and normalizes MongoDB inputs."""
    
    # Maximum string length for various inputs
    MAX_STRING_LENGTH = 1000
    MAX_QUERY_DEPTH = 10
    MAX_DOCUMENT_SIZE = 16 * 1024 * 1024  # 16MB MongoDB document limit
    
    @classmethod
    def sanitize_string(cls, value: str) -> str:
        """Sanitize string inputs."""
        if not isinstance(value, str):
            raise ValueError("Expected string input")
        
        if len(value) > cls.MAX_STRING_LENGTH:
            raise ValueError(f"String exceeds maximum length {cls.MAX_STRING_LENGTH}")
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        return sanitized.strip()
    
    @classmethod
    def sanitize_query(cls, query: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize MongoDB query structure."""
        cls._check_depth(query, 0)
        return cls._sanitize_dict(query)
    
    @classmethod
    def sanitize_document(cls, document: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize document for insertion/update."""
        import json
        doc_size = len(json.dumps(document, default=str))
        if doc_size > cls.MAX_DOCUMENT_SIZE:
            raise ValueError(f"Document size {doc_size} exceeds limit {cls.MAX_DOCUMENT_SIZE}")
        
        cls._check_depth(document, 0)
        return cls._sanitize_dict(document)
    
    @classmethod
    def _check_depth(cls, obj: Any, current_depth: int) -> None:
        """Check nesting depth to prevent deep recursion."""
        if current_depth > cls.MAX_QUERY_DEPTH:
            raise ValueError(f"Structure exceeds maximum depth {cls.MAX_QUERY_DEPTH}")
        
        if isinstance(obj, dict):
            for value in obj.values():
                cls._check_depth(value, current_depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                cls._check_depth(item, current_depth + 1)
    
    @classmethod
    def _sanitize_dict(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary."""
        sanitized = {}
        for key, value in obj.items():
            # Sanitize keys
            clean_key = cls.sanitize_string(key) if isinstance(key, str) else key
            
            # Sanitize values
            if isinstance(value, str):
                sanitized[clean_key] = cls.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = cls._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[clean_key] = [
                    cls._sanitize_dict(item) if isinstance(item, dict)
                    else cls.sanitize_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[clean_key] = value
        
        return sanitized