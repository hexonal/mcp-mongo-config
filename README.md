# 🍃 MongoDB MCP Server

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12%2B-green)](https://gofastmcp.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-green)](https://www.mongodb.com/)

A powerful Model Context Protocol (MCP) server for MongoDB operations, enabling Claude to interact with MongoDB databases through a secure, feature-rich interface.

## ✨ Features

- 🔒 **Security First**: Read-only by default with optional dangerous mode
- 🚀 **High Performance**: Async operations using Motor driver
- 🌐 **Cluster Support**: Both standalone and replica set deployments
- 🛠️ **Rich Toolset**: 13 specialized tools for complete MongoDB operations
- 🎯 **Smart Validation**: JSON schema validation and query sanitization
- 🌍 **Internationalization**: Full Chinese language support
- 📡 **Standards Compliant**: Implements MCP 2024-11-05 specification

## 📋 Requirements

- **Python**: 3.8+ (recommended 3.10+)
- **MongoDB**: 4.4+ 
- **Network**: Access to MongoDB instance or cluster

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install mongodb-mcp
```

### Development Installation
```bash
git clone https://github.com/hexonal/mcp-mongo-config.git
cd mcp-mongo-config
pip install -e .
```

### Using uv (Fast)
```bash
uv add mongodb-mcp
```

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_HOST` | `localhost` | MongoDB host address (supports cluster: `host1,host2,host3`) |
| `MONGODB_PORT` | `27017` | MongoDB port |
| `MONGODB_DATABASE` | `default` | Default database name |
| `MONGODB_USERNAME` | `None` | Username for authentication |
| `MONGODB_PASSWORD` | `None` | Password for authentication |
| `MONGODB_AUTH_DB` | `admin` | Authentication database |
| `MONGODB_URI` | `None` | Complete connection URI (overrides other params) |
| `MONGODB_ALLOW_DANGEROUS` | `false` | Enable write operations |
| `MONGODB_MAX_DOCUMENTS` | `1000` | Maximum documents per query |
| `MONGODB_TIMEOUT` | `30` | Query timeout in seconds |

### 🖥️ Claude Desktop Setup

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mongodb": {
      "command": "python",
      "args": ["-m", "mongodb_mcp"],
      "env": {
        "MONGODB_HOST": "your-mongodb-host",
        "MONGODB_PORT": "27017",
        "MONGODB_DATABASE": "your-database",
        "MONGODB_USERNAME": "your-username",
        "MONGODB_PASSWORD": "your-password",
        "MONGODB_AUTH_DB": "admin"
      }
    }
  }
}
```

### 🔗 Connection Modes

**Standalone Mode**
```bash
MONGODB_HOST=localhost
MONGODB_PORT=27017
```

**Cluster Mode**
```bash
MONGODB_HOST=node1.example.com,node2.example.com,node3.example.com
# Automatically adds: replicaSet=rs0&readPreference=secondaryPreferred
```

## 🛠️ Available Tools

### 📊 Database Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `list_databases` | List all available databases | None |
| `get_database_stats` | Get database statistics | `database` |

### 📦 Collection Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `list_collections` | List collections in database | `database` |
| `describe_collection` | Get collection metadata | `database`, `collection` |
| `get_collection_stats` | Get collection statistics | `database`, `collection` |
| `list_indexes` | List collection indexes | `database`, `collection` |

### 📄 Document Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `find_documents` | Query documents | `database`, `collection`, `query?`, `limit?`, `sort?` |
| `find_one_document` | Find single document | `database`, `collection`, `query?` |
| `count_documents` | Count matching documents | `database`, `collection`, `query?` |

### 🔧 Aggregation Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `aggregate_pipeline` | Execute aggregation pipeline | `database`, `collection`, `pipeline`, `limit?` |

### ⚠️ Write Operations (Dangerous Mode)
| Tool | Description | Parameters |
|------|-------------|------------|
| `insert_document` | Insert document | `database`, `collection`, `document` |
| `update_document` | Update documents | `database`, `collection`, `query`, `update` |
| `delete_document` | Delete documents | `database`, `collection`, `query` |
| `create_index` | Create index | `database`, `collection`, `keys`, `options?` |

## 💡 Usage Examples

### Basic Operations
```python
# Explore your databases
databases = await list_databases()

# Find recent orders
orders = await find_documents(
    database="ecommerce",
    collection="orders",
    query={"created_at": {"$gte": "2025-08-01"}},
    sort={"created_at": -1},
    limit=10
)
```

### Advanced Aggregations
```python
# Sales analysis by category
pipeline = [
    {"$match": {"status": "completed"}},
    {"$group": {
        "_id": "$category", 
        "revenue": {"$sum": "$amount"},
        "orders": {"$sum": 1}
    }},
    {"$sort": {"revenue": -1}}
]

results = await aggregate_pipeline(
    database="ecommerce",
    collection="orders", 
    pipeline=pipeline
)
```

## 🔒 Security Features

### 🛡️ Safe Mode (Default)
- Read-only operations only
- Query operator validation (blocks `$where`, `$expr`)
- Input sanitization and depth limits
- Result size restrictions

### ⚠️ Dangerous Mode
- Requires `MONGODB_ALLOW_DANGEROUS=true`
- Enables write operations
- Additional audit logging recommended
- Use only in trusted environments

### 🔍 Query Protection
```python
# ✅ Safe - These work in default mode
{"price": {"$gt": 100}}
{"status": {"$in": ["active", "pending"]}}

# ❌ Blocked - Requires dangerous mode
{"$where": "this.price > 100"}
{"$expr": {"$gt": ["$price", 100]}}
```

## 🚀 Quick Start

1. **Install the package**
   ```bash
   pip install mongodb-mcp
   ```

2. **Set environment variables**
   ```bash
   export MONGODB_HOST=your-mongodb-host
   export MONGODB_DATABASE=your-database
   export MONGODB_USERNAME=your-username
   export MONGODB_PASSWORD=your-password
   ```

3. **Add to Claude Desktop config**
   ```json
   {
     "mcpServers": {
       "mongodb": {
         "command": "python",
         "args": ["-m", "mongodb_mcp"],
         "env": {
           "MONGODB_HOST": "your-host",
           "MONGODB_DATABASE": "your-db"
         }
       }
     }
   }
   ```

4. **Start using in Claude**
   ```
   Can you list all databases in MongoDB?
   Show me the collections in the 'ecommerce' database.
   Find products with price greater than $100.
   ```

## 🏗️ Development

### Setup Development Environment
```bash
git clone https://github.com/hexonal/mcp-mongo-config.git
cd mcp-mongo-config
pip install -e ".[dev]"
```

### Code Quality
```bash
# Format code
black src/
isort src/

# Type checking  
mypy src/

# Run tests
pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆚 Comparison with Other MCP Servers

| Feature | MongoDB MCP | MySQL MCP | Redis MCP |
|---------|-------------|-----------|-----------|
| **Query Language** | MongoDB/JSON | SQL | Redis Commands |
| **Data Model** | Document | Relational | Key-Value |
| **Tools Count** | 13 | 4 | 8 |
| **Async Support** | ✅ Motor | ✅ aiomysql | ✅ aioredis |
| **Security** | JSON validation | AST parsing | Command filtering |
| **Aggregation** | ✅ Pipelines | ✅ SQL | ❌ Limited |