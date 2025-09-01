# MongoDB MCP Server

A Model Context Protocol (MCP) server for MongoDB operations using the FastMCP framework.

## Features

- **Secure by Default**: Read-only operations with optional dangerous mode for writes
- **Comprehensive Tools**: 13 specialized tools for MongoDB operations
- **JSON Schema Validation**: Security through input validation and sanitization
- **Async Operations**: High-performance async MongoDB operations using Motor
- **FastMCP Integration**: Built on FastMCP 2.0 with decorator-based tool registration

## Installation

```bash
pip install mongodb-mcp
```

## Configuration

### Environment Variables

```bash
MONGODB_URI="mongodb://localhost:27017"          # Connection string
MONGODB_DATABASE="default"                       # Default database
MONGODB_ALLOW_DANGEROUS="false"                  # Enable write operations
MONGODB_MAX_DOCUMENTS="1000"                     # Result limit
MONGODB_TIMEOUT="30"                             # Query timeout (seconds)
```

### Claude Desktop Integration

```json
{
  "mcpServers": {
    "mongodb": {
      "command": "python",
      "args": ["-m", "mongodb_mcp"],
      "env": {
        "MONGODB_URI": "mongodb://localhost:27017",
        "MONGODB_DATABASE": "myapp",
        "MONGODB_MAX_DOCUMENTS": "500"
      }
    }
  }
}
```

## Available Tools

### Database Operations
- `list_databases` - List all available databases
- `get_database_stats` - Get database statistics and metadata

### Collection Operations  
- `list_collections` - List collections in a database
- `describe_collection` - Get collection schema, indexes, and metadata
- `get_collection_stats` - Get collection performance statistics
- `list_indexes` - List all indexes for a collection

### Document Operations (Read-Only)
- `find_documents` - Query documents with filtering, sorting, pagination
- `find_one_document` - Find single document
- `count_documents` - Efficient document counting

### Aggregation Operations
- `aggregate_pipeline` - Execute aggregation pipelines

### Write Operations (Dangerous Mode Only)
- `insert_document` - Insert documents
- `update_document` - Update documents
- `delete_document` - Delete documents
- `create_index` - Create database indexes

## Usage Examples

### Basic Queries
```python
# List all databases
databases = await list_databases()

# Find active users
users = await find_documents(
    database="myapp",
    collection="users",
    query={"status": "active"},
    limit=50
)

# Count orders from last month
order_count = await count_documents(
    database="ecommerce",
    collection="orders",
    query={"created_at": {"$gte": "2025-08-01"}}
)
```

### Aggregation Pipelines
```python
# Revenue analysis
revenue_pipeline = [
    {"$match": {"status": "completed"}},
    {"$group": {
        "_id": "$category",
        "total_revenue": {"$sum": "$amount"},
        "order_count": {"$sum": 1}
    }},
    {"$sort": {"total_revenue": -1}}
]

results = await aggregate_pipeline(
    database="ecommerce",
    collection="orders",
    pipeline=revenue_pipeline
)
```

### Write Operations (Dangerous Mode)
```python
# Requires MONGODB_ALLOW_DANGEROUS="true"

# Insert new user
result = await insert_document(
    database="myapp",
    collection="users",
    document={"name": "John Doe", "email": "john@example.com"}
)

# Update user status
update_result = await update_document(
    database="myapp",
    collection="users",
    query={"email": "john@example.com"},
    update={"$set": {"status": "verified"}}
)
```

## Security Features

### Query Validation
- **Safe Operators**: Whitelist of allowed MongoDB query operators
- **Dangerous Operators**: `$where`, `$expr`, `$jsonSchema` require explicit permission
- **Input Sanitization**: Removes control characters and validates structure
- **Depth Limits**: Prevents deep nesting attacks

### Aggregation Security
- **Stage Filtering**: Whitelist of safe aggregation stages
- **Pipeline Limits**: Maximum number of stages configurable
- **Output Prevention**: Blocks `$out`, `$merge` stages in safe mode

### Write Protection
- **Read-Only Default**: Write operations disabled by default
- **Explicit Enablement**: Requires `MONGODB_ALLOW_DANGEROUS=true`
- **Operation Logging**: All write operations can be logged

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

## Architecture

The server follows a modular design:

- **Security Layer**: Input validation and sanitization
- **Handler Layer**: Operation-specific business logic  
- **Connection Layer**: MongoDB client lifecycle management
- **Server Layer**: FastMCP tool registration and coordination

## Comparison with MySQL MCP

| Feature | MySQL MCP | MongoDB MCP |
|---------|-----------|-------------|
| **Framework** | FastMCP 2.0 | FastMCP 2.0 |
| **Security** | AST SQL parsing | JSON schema validation |
| **Connection** | aiomysql | motor |
| **Operations** | 4 SQL-focused tools | 13 MongoDB-specialized tools |
| **Query Language** | SQL | MongoDB query language + aggregation |
| **Schema** | Fixed relational | Flexible document schema |

## License

MIT License