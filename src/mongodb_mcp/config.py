"""MongoDB MCP服务器配置管理模块."""

import os
from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class MongoDBConfig(BaseSettings):
    """MongoDB MCP服务器配置类."""
    
    # MongoDB连接参数
    mongodb_host: str = Field(
        default="localhost",
        description="MongoDB服务器主机地址"
    )
    mongodb_port: int = Field(
        default=27017,
        description="MongoDB服务器端口"
    )
    mongodb_database: str = Field(
        default="default", 
        description="默认数据库名称"
    )
    mongodb_username: Optional[str] = Field(
        default=None,
        description="MongoDB用户名"
    )
    mongodb_password: Optional[str] = Field(
        default=None,
        description="MongoDB密码"
    )
    mongodb_auth_db: str = Field(
        default="admin",
        description="认证数据库"
    )
    
    # 兼容URI格式配置
    mongodb_uri: Optional[str] = Field(
        default=None,
        description="完整的MongoDB连接URI（优先于其他参数）"
    )
    
    # 安全和限制配置
    mongodb_allow_dangerous: bool = Field(
        default=False,
        description="启用写操作（危险模式）"
    )
    mongodb_max_documents: int = Field(
        default=1000,
        description="查询返回的最大文档数"
    )
    mongodb_timeout: int = Field(
        default=30,
        description="查询超时时间（秒）"
    )
    mongodb_max_pipeline_stages: int = Field(
        default=20,
        description="聚合管道最大阶段数"
    )
    
    @property
    def connection_uri(self) -> str:
        """构建MongoDB连接URI，支持集群和单机模式."""
        if self.mongodb_uri:
            return self.mongodb_uri
        
        # 构建认证部分
        if self.mongodb_username and self.mongodb_password:
            auth_part = f"{self.mongodb_username}:{self.mongodb_password}@"
        else:
            auth_part = ""
        
        # 构建主机部分（支持集群模式的多主机）
        if ',' in self.mongodb_host:
            # 集群模式：多个主机地址
            hosts = self.mongodb_host.split(',')
            host_part = ','.join([f"{host.strip()}:{self.mongodb_port}" for host in hosts])
        else:
            # 单机模式：单个主机地址
            host_part = f"{self.mongodb_host}:{self.mongodb_port}"
        
        # 构建参数部分
        params = []
        if self.mongodb_username and self.mongodb_password:
            params.append(f"authSource={self.mongodb_auth_db}")
        
        # 集群模式建议的参数
        if ',' in self.mongodb_host:
            params.extend([
                "replicaSet=rs0",  # 默认副本集名称
                "readPreference=secondaryPreferred",  # 读优先级
                "retryWrites=true"  # 重试写操作
            ])
        
        param_string = "&".join(params)
        if param_string:
            param_string = "?" + param_string
        
        return f"mongodb://{auth_part}{host_part}/{self.mongodb_database}{param_string}"
    
    @property 
    def is_cluster_mode(self) -> bool:
        """检测是否为集群模式."""
        return ',' in self.mongodb_host or 'replicaSet' in (self.mongodb_uri or '')
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_config() -> MongoDBConfig:
    """获取MongoDB MCP配置实例."""
    return MongoDBConfig()