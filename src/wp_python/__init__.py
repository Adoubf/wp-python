"""
WordPress REST API Python 客户端库

这是一个基于最新WordPress官方文档构建的Python客户端库，
支持WordPress REST API的所有核心功能。

主要特性：
- 完整的API端点支持
- 同步和异步操作
- 类型安全和数据验证
- 多种认证方式
- 简体中文注释和文档

使用示例：
    from wp_python import WordPress
    
    # 创建客户端实例
    wp = WordPress('https://your-site.com', username='用户名', password='应用程序密码')
    
    # 获取文章列表
    posts = wp.posts.list()
    
    # 创建新文章
    new_post = wp.posts.create(title='标题', content='内容')
"""

from .wordpress import WordPress, AsyncWordPress
from .core.exceptions import (
    WordPressError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    PermissionError,
    RateLimitError
)

# 版本信息
__version__ = "0.2.0"
__author__ = "haoyue"
__email__ = "haoyue@coralera.org"

# 导出主要类和异常
__all__ = [
    "WordPress",
    "AsyncWordPress",
    "WordPressError", 
    "AuthenticationError",
    "NotFoundError",
    "ValidationError", 
    "PermissionError",
    "RateLimitError"
]