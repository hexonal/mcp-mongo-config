"""MongoDB MCP server implementation using FastMCP."""

import asyncio
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

from .config import get_config, MongoDBConfig
from .connection import MongoDBConnection
from .handlers import DatabaseHandler, CollectionHandler, DocumentHandler, AggregationHandler


class MongoDBMCPServer:
    """MongoDB MCP server class."""
    
    def __init__(self):
        self.config = get_config()
        self.connection = MongoDBConnection(self.config)
        
        # Initialize handlers
        self.db_handler: Optional[DatabaseHandler] = None
        self.collection_handler: Optional[CollectionHandler] = None
        self.document_handler: Optional[DocumentHandler] = None
        self.aggregation_handler: Optional[AggregationHandler] = None
    
    async def setup(self):
        """Initialize MongoDB connection and handlers."""
        await self.connection.connect()
        
        self.db_handler = DatabaseHandler(self.connection.client)
        self.collection_handler = CollectionHandler(self.connection.client)
        self.document_handler = DocumentHandler(
            self.connection.client, 
            self.config.mongodb_allow_dangerous
        )
        self.aggregation_handler = AggregationHandler(
            self.connection.client,
            self.config.mongodb_allow_dangerous
        )
    
    async def cleanup(self):
        """Cleanup connections."""
        await self.connection.disconnect()


# Create FastMCP app
mcp = FastMCP("MongoDB MCP Server")

# Global server instance - will be initialized when first tool is called
server_instance = None


async def ensure_server_initialized():
    """确保服务器已初始化."""
    global server_instance
    if server_instance is None:
        server_instance = MongoDBMCPServer()
        await server_instance.setup()


# Database Operations
@mcp.tool
async def list_databases() -> List[Dict[str, Any]]:
    """List all available MongoDB databases."""
    await ensure_server_initialized()
    return await server_instance.db_handler.list_databases()


@mcp.tool
async def get_database_stats(database: str) -> Dict[str, Any]:
    """Get comprehensive database statistics."""
    await ensure_server_initialized()
    return await server_instance.db_handler.get_database_stats(database)


# Collection Operations  
@mcp.tool
async def list_collections(database: str) -> List[Dict[str, Any]]:
    """List collections in specified database."""
    await ensure_server_initialized()
    return await server_instance.collection_handler.list_collections(database)


@mcp.tool
async def describe_collection(database: str, collection: str) -> Dict[str, Any]:
    """Get collection schema, indexes, and metadata."""
    await ensure_server_initialized()
    return await server_instance.collection_handler.describe_collection(database, collection)


@mcp.tool
async def get_collection_stats(database: str, collection: str) -> Dict[str, Any]:
    """Get collection performance statistics."""
    await ensure_server_initialized()
    return await server_instance.collection_handler.get_collection_stats(database, collection)


@mcp.tool
async def list_indexes(database: str, collection: str) -> List[Dict[str, Any]]:
    """List all indexes for a collection."""
    await ensure_server_initialized()
    return await server_instance.collection_handler.list_indexes(database, collection)


# Document Operations (Read)
@mcp.tool
async def find_documents(
    database: str,
    collection: str,
    query: Dict[str, Any] = None,
    projection: Dict[str, Any] = None,
    sort: Dict[str, Any] = None,
    limit: int = 100,
    skip: int = 0
) -> Dict[str, Any]:
    """Find documents matching query criteria."""
    await ensure_server_initialized()
    return await server_instance.document_handler.find_documents(
        database, collection, query, projection, sort, limit, skip
    )


@mcp.tool
async def find_one_document(
    database: str,
    collection: str,
    query: Dict[str, Any] = None,
    projection: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """Find single document matching criteria."""
    await ensure_server_initialized()
    return await server_instance.document_handler.find_one_document(
        database, collection, query, projection
    )


@mcp.tool
async def count_documents(
    database: str,
    collection: str,
    query: Dict[str, Any] = None
) -> int:
    """Count documents matching query."""
    await ensure_server_initialized()
    return await server_instance.document_handler.count_documents(database, collection, query)


# Aggregation Operations
@mcp.tool
async def aggregate_pipeline(
    database: str,
    collection: str,
    pipeline: List[Dict[str, Any]],
    limit: int = 100
) -> Dict[str, Any]:
    """Execute MongoDB aggregation pipeline."""
    await ensure_server_initialized()
    return await server_instance.aggregation_handler.aggregate_pipeline(
        database, collection, pipeline, limit, server_instance.config.mongodb_max_pipeline_stages
    )


# Write Operations (Dangerous Mode Only)
@mcp.tool
async def insert_document(
    database: str,
    collection: str,
    document: Dict[str, Any]
) -> Dict[str, Any]:
    """Insert single document (requires dangerous mode)."""
    await ensure_server_initialized()
    return await server_instance.document_handler.insert_document(database, collection, document)


@mcp.tool
async def update_document(
    database: str,
    collection: str,
    query: Dict[str, Any],
    update: Dict[str, Any],
    upsert: bool = False
) -> Dict[str, Any]:
    """Update documents matching query (requires dangerous mode)."""
    await ensure_server_initialized()
    return await server_instance.document_handler.update_document(
        database, collection, query, update, upsert
    )


@mcp.tool
async def delete_document(
    database: str,
    collection: str,
    query: Dict[str, Any]
) -> Dict[str, Any]:
    """Delete documents matching query (requires dangerous mode)."""
    await ensure_server_initialized()
    return await server_instance.document_handler.delete_document(database, collection, query)


@mcp.tool
async def create_index(
    database: str,
    collection: str,
    keys: Dict[str, Any],
    name: str = None,
    unique: bool = False,
    background: bool = True
) -> Dict[str, Any]:
    """Create index on collection (requires dangerous mode)."""
    await ensure_server_initialized()
    kwargs = {'background': background}
    if name:
        kwargs['name'] = name
    if unique:
        kwargs['unique'] = unique
        
    return await server_instance.aggregation_handler.create_index(
        database, collection, keys, **kwargs
    )


def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()