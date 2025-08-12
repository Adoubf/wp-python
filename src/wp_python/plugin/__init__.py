"""
WordPress REST API Python客户端插件系统

提供可扩展的插件架构，支持用户自定义插件开发。
"""

from .base import BasePlugin, PluginManager, get_plugin_manager
from .fastapi import FastAPIPlugin

__all__ = [
    "BasePlugin",
    "PluginManager",
    "get_plugin_manager", 
    "FastAPIPlugin"
]