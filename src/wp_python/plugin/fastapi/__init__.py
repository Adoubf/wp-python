"""
WordPress REST API FastAPI 插件

提供基于FastAPI的Web服务框架，高度封装，方便用户快速构建WordPress API服务。
"""

from .plugin import FastAPIPlugin
from .server import FastAPIServer
from .middleware import WordPressMiddleware
from .routes import WordPressRouter

__all__ = [
    "FastAPIPlugin",
    "FastAPIServer", 
    "WordPressMiddleware",
    "WordPressRouter"
]