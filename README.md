# 🍃 MongoDB MCP Server | MongoDB MCP 服务器

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12%2B-green)](https://gofastmcp.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-green)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Model Context Protocol (MCP) server for MongoDB operations, enabling Claude to interact with MongoDB databases through a secure, feature-rich interface.

功能强大的MongoDB模型上下文协议(MCP)服务器，让Claude能够通过安全、功能丰富的接口与MongoDB数据库交互。

---

## 🌐 Language | 语言版本

- [English Documentation](#english-documentation)
- [中文文档](#中文文档)

---

## English Documentation

### ✨ Features

- 🔒 **Security First**: Read-only by default with optional dangerous mode
- 🚀 **High Performance**: Async operations using Motor driver
- 🌐 **Cluster Support**: Both standalone and replica set deployments
- 🛠️ **Rich Toolset**: 13 specialized tools for complete MongoDB operations
- 🎯 **Smart Validation**: JSON schema validation and query sanitization
- 🌍 **Internationalization**: Full Chinese language support
- 📡 **Standards Compliant**: Implements MCP 2024-11-05 specification

### 📋 Requirements

- **Python**: 3.8+ (recommended 3.10+)
- **MongoDB**: 4.4+ 
- **Network**: Access to MongoDB instance or cluster

### 📦 Installation

#### From GitHub (Recommended)
```bash
# Using uvx (recommended)
uvx --from git+https://github.com/hexonal/mcp-mongo-config.git mongodb-mcp

# Using pip
pip install git+https://github.com/hexonal/mcp-mongo-config.git
```

#### Development Installation
```bash
git clone https://github.com/hexonal/mcp-mongo-config.git
cd mcp-mongo-config
pip install -e ".[dev]"
```

#### Using uv (Development)
```bash
git clone https://github.com/hexonal/mcp-mongo-config.git
cd mcp-mongo-config
uv sync --dev
```

### ⚙️ Configuration

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

#### 🖥️ Claude Desktop Setup

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mongodb": {
      "command": "uvx",
      "args": [
        "--from", 
        "git+https://github.com/hexonal/mcp-mongo-config.git",
        "mongodb-mcp"
      ],
      "env": {
        "MONGODB_HOST": "your-mongodb-host",
        "MONGODB_PORT": "27017",
        "MONGODB_DATABASE": "your-database",
        "MONGODB_USERNAME": "your-username",
        "MONGODB_PASSWORD": "your-password",
        "MONGODB_AUTH_DB": "admin",
        "MONGODB_ALLOW_DANGEROUS": "false"
      }
    }
  }
}
```

### 🛠️ Available Tools

#### 📊 Database Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `list_databases` | List all available databases | None |
| `get_database_stats` | Get database statistics | `database` |

#### 📦 Collection Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `list_collections` | List collections in database | `database` |
| `describe_collection` | Get collection metadata | `database`, `collection` |
| `get_collection_stats` | Get collection statistics | `database`, `collection` |
| `list_indexes` | List collection indexes | `database`, `collection` |

#### 📄 Document Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `find_documents` | Query documents | `database`, `collection`, `query?`, `limit?`, `sort?` |
| `find_one_document` | Find single document | `database`, `collection`, `query?` |
| `count_documents` | Count matching documents | `database`, `collection`, `query?` |

#### 🔧 Aggregation Operations
| Tool | Description | Parameters |
|------|-------------|------------|
| `aggregate_pipeline` | Execute aggregation pipeline | `database`, `collection`, `pipeline`, `limit?` |

#### ⚠️ Write Operations (Dangerous Mode)
| Tool | Description | Parameters |
|------|-------------|------------|
| `insert_document` | Insert document | `database`, `collection`, `document` |
| `update_document` | Update documents | `database`, `collection`, `query`, `update` |
| `delete_document` | Delete documents | `database`, `collection`, `query` |
| `create_index` | Create index | `database`, `collection`, `keys`, `options?` |

### 💡 Usage Examples

#### Basic Operations
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

#### Advanced Aggregations
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

### 🔒 Security Features

#### 🛡️ Safe Mode (Default)
- Read-only operations only
- Query operator validation (blocks `$where`, `$expr`)
- Input sanitization and depth limits
- Result size restrictions

#### ⚠️ Dangerous Mode
- Requires `MONGODB_ALLOW_DANGEROUS=true`
- Enables write operations
- Additional audit logging recommended
- Use only in trusted environments

#### 🔍 Query Protection
```python
# ✅ Safe - These work in default mode
{"price": {"$gt": 100}}
{"status": {"$in": ["active", "pending"]}}

# ❌ Blocked - Requires dangerous mode
{"$where": "this.price > 100"}
{"$expr": {"$gt": ["$price", 100]}}
```

### 🚀 Quick Start

1. **Install the package**
   ```bash
   uvx --from git+https://github.com/hexonal/mcp-mongo-config.git mongodb-mcp
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
         "command": "uvx",
         "args": [
           "--from", 
           "git+https://github.com/hexonal/mcp-mongo-config.git",
           "mongodb-mcp"
         ],
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

### 🏗️ Development

#### Setup Development Environment
```bash
git clone https://github.com/hexonal/mcp-mongo-config.git
cd mcp-mongo-config
pip install -e ".[dev]"
```

#### Code Quality
```bash
# Format code
black src/
isort src/

# Type checking  
mypy src/

# Run tests
pytest
```

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

### 🆚 Comparison with Other MCP Servers

| Feature | MongoDB MCP | MySQL MCP | Redis MCP |
|---------|-------------|-----------|-----------|
| **Query Language** | MongoDB/JSON | SQL | Redis Commands |
| **Data Model** | Document | Relational | Key-Value |
| **Tools Count** | 13 | 4 | 8 |
| **Async Support** | ✅ Motor | ✅ aiomysql | ✅ aioredis |
| **Security** | JSON validation | AST parsing | Command filtering |
| **Aggregation** | ✅ Pipelines | ✅ SQL | ❌ Limited |

---

# 中文文档

## ✨ 特性

- 🔒 **安全优先**: 默认只读模式，可选危险操作模式
- 🚀 **高性能**: 使用Motor驱动程序的异步操作
- 🌐 **集群支持**: 支持单机和副本集部署
- 🛠️ **丰富的工具集**: 13个专业工具完成完整的MongoDB操作
- 🎯 **智能验证**: JSON模式验证和查询清理
- 🌍 **国际化**: 完整的中文语言支持
- 📡 **标准兼容**: 实现MCP 2024-11-05规范

## 📋 系统要求

- **Python**: 3.8+ (推荐 3.10+)
- **MongoDB**: 4.4+ 
- **网络**: 访问MongoDB实例或集群

## 📦 安装

### 从GitHub安装（推荐）
```bash
# 使用uvx（推荐）
uvx --from git+https://github.com/hexonal/mcp-mongo-config.git mongodb-mcp

# 使用pip
pip install git+https://github.com/hexonal/mcp-mongo-config.git
```

### 开发环境安装
```bash
git clone https://github.com/hexonal/mcp-mongo-config.git
cd mcp-mongo-config
pip install -e ".[dev]"
```

### 使用uv（开发模式）
```bash
git clone https://github.com/hexonal/mcp-mongo-config.git
cd mcp-mongo-config
uv sync --dev
```

## ⚙️ 配置

| 变量 | 默认值 | 描述 |
|------|---------|-----|
| `MONGODB_HOST` | `localhost` | MongoDB主机地址（支持集群：`主机1,主机2,主机3`） |
| `MONGODB_PORT` | `27017` | MongoDB端口 |
| `MONGODB_DATABASE` | `default` | 默认数据库名称 |
| `MONGODB_USERNAME` | `None` | 认证用户名 |
| `MONGODB_PASSWORD` | `None` | 认证密码 |
| `MONGODB_AUTH_DB` | `admin` | 认证数据库 |
| `MONGODB_URI` | `None` | 完整连接URI（覆盖其他参数） |
| `MONGODB_ALLOW_DANGEROUS` | `false` | 启用写操作 |
| `MONGODB_MAX_DOCUMENTS` | `1000` | 每次查询最大文档数 |
| `MONGODB_TIMEOUT` | `30` | 查询超时时间（秒） |

### 🖥️ Claude Desktop配置

在Claude Desktop配置中添加：

```json
{
  "mcpServers": {
    "mongodb": {
      "command": "uvx",
      "args": [
        "--from", 
        "git+https://github.com/hexonal/mcp-mongo-config.git",
        "mongodb-mcp"
      ],
      "env": {
        "MONGODB_HOST": "your-mongodb-host",
        "MONGODB_PORT": "27017",
        "MONGODB_DATABASE": "your-database",
        "MONGODB_USERNAME": "your-username",
        "MONGODB_PASSWORD": "your-password",
        "MONGODB_AUTH_DB": "admin",
        "MONGODB_ALLOW_DANGEROUS": "false"
      }
    }
  }
}
```

### 🔗 连接模式

**单机模式**
```bash
MONGODB_HOST=localhost
MONGODB_PORT=27017
```

**集群模式**
```bash
MONGODB_HOST=节点1.example.com,节点2.example.com,节点3.example.com
# 自动添加: replicaSet=rs0&readPreference=secondaryPreferred
```

## 🛠️ 可用工具

### 📊 数据库操作
| 工具 | 描述 | 参数 |
|------|-----|------|
| `list_databases` | 列出所有可用数据库 | 无 |
| `get_database_stats` | 获取数据库统计信息 | `database` |

### 📦 集合操作
| 工具 | 描述 | 参数 |
|------|-----|------|
| `list_collections` | 列出数据库中的集合 | `database` |
| `describe_collection` | 获取集合元数据 | `database`, `collection` |
| `get_collection_stats` | 获取集合统计信息 | `database`, `collection` |
| `list_indexes` | 列出集合索引 | `database`, `collection` |

### 📄 文档操作
| 工具 | 描述 | 参数 |
|------|-----|------|
| `find_documents` | 查询文档 | `database`, `collection`, `query?`, `limit?`, `sort?` |
| `find_one_document` | 查找单个文档 | `database`, `collection`, `query?` |
| `count_documents` | 统计匹配文档数量 | `database`, `collection`, `query?` |

### 🔧 聚合操作
| 工具 | 描述 | 参数 |
|------|-----|------|
| `aggregate_pipeline` | 执行聚合管道 | `database`, `collection`, `pipeline`, `limit?` |

### ⚠️ 写操作（危险模式）
| 工具 | 描述 | 参数 |
|------|-----|------|
| `insert_document` | 插入文档 | `database`, `collection`, `document` |
| `update_document` | 更新文档 | `database`, `collection`, `query`, `update` |
| `delete_document` | 删除文档 | `database`, `collection`, `query` |
| `create_index` | 创建索引 | `database`, `collection`, `keys`, `options?` |

## 💡 使用示例

### 基本操作
```python
# 探索数据库
databases = await list_databases()

# 查找最近订单
orders = await find_documents(
    database="ecommerce",
    collection="orders",
    query={"created_at": {"$gte": "2025-08-01"}},
    sort={"created_at": -1},
    limit=10
)
```

### 高级聚合
```python
# 按类别分析销售
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

## 🔒 安全特性

### 🛡️ 安全模式（默认）
- 仅允许只读操作
- 查询操作符验证（阻止`$where`、`$expr`）
- 输入清理和深度限制
- 结果大小限制

### ⚠️ 危险模式
- 需要设置`MONGODB_ALLOW_DANGEROUS=true`
- 启用写操作
- 建议增加审计日志
- 仅在可信环境中使用

### 🔍 查询保护
```python
# ✅ 安全 - 在默认模式下可用
{"price": {"$gt": 100}}
{"status": {"$in": ["active", "pending"]}}

# ❌ 阻止 - 需要危险模式
{"$where": "this.price > 100"}
{"$expr": {"$gt": ["$price", 100]}}
```

## 🚀 快速开始

1. **安装包**
   ```bash
   uvx --from git+https://github.com/hexonal/mcp-mongo-config.git mongodb-mcp
   ```

2. **设置环境变量**
   ```bash
   export MONGODB_HOST=your-mongodb-host
   export MONGODB_DATABASE=your-database
   export MONGODB_USERNAME=your-username
   export MONGODB_PASSWORD=your-password
   ```

3. **添加到Claude Desktop配置**
   ```json
   {
     "mcpServers": {
       "mongodb": {
         "command": "uvx",
         "args": [
           "--from", 
           "git+https://github.com/hexonal/mcp-mongo-config.git",
           "mongodb-mcp"
         ],
         "env": {
           "MONGODB_HOST": "your-host",
           "MONGODB_DATABASE": "your-db"
         }
       }
     }
   }
   ```

4. **在Claude中开始使用**
   ```
   能否列出MongoDB中的所有数据库？
   显示'ecommerce'数据库中的集合。
   查找价格大于100元的产品。
   ```

## 🏗️ 开发

### 设置开发环境
```bash
git clone https://github.com/hexonal/mcp-mongo-config.git
cd mcp-mongo-config
pip install -e ".[dev]"
```

### 代码质量
```bash
# 格式化代码
black src/
isort src/

# 类型检查  
mypy src/

# 运行测试
pytest
```

## 🤝 贡献

1. Fork仓库
2. 创建功能分支
3. 进行更改
4. 为新功能添加测试
5. 确保所有测试通过
6. 提交拉取请求

## 📄 许可证

MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 🆚 与其他MCP服务器比较

| 特性 | MongoDB MCP | MySQL MCP | Redis MCP |
|------|-------------|-----------|-----------|
| **查询语言** | MongoDB/JSON | SQL | Redis命令 |
| **数据模型** | 文档型 | 关系型 | 键值型 |
| **工具数量** | 13 | 4 | 8 |
| **异步支持** | ✅ Motor | ✅ aiomysql | ✅ aioredis |
| **安全性** | JSON验证 | AST解析 | 命令过滤 |
| **聚合功能** | ✅ 管道 | ✅ SQL | ❌ 有限 |