"""
FastAPI 插件实现

提供完整的FastAPI Web服务功能，包括自动路由、中间件和服务器管理。
"""

from typing import Dict, Any, Optional
import asyncio
from fastapi import FastAPI

from ..base import BasePlugin
from .server import FastAPIServer
from .middleware import WordPressMiddleware
from .routes import WordPressRouter


class FastAPIPlugin(BasePlugin):
    """
    FastAPI插件
    
    提供基于FastAPI的Web服务功能，支持：
    - 自动WordPress API路由
    - 中间件支持
    - Gunicorn + Uvicorn部署
    - 热重载开发模式
    """
    
    def __init__(self):
        """初始化FastAPI插件"""
        super().__init__("fastapi", "1.0.0")
        self.server: Optional[FastAPIServer] = None
        self.app: Optional[FastAPI] = None
        self._server_task: Optional[asyncio.Task] = None
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化插件
        
        参数:
            config: 插件配置
                - host: 服务器主机，默认 "0.0.0.0"
                - port: 服务器端口，默认 8000
                - debug: 调试模式，默认 False
                - reload: 热重载，默认 False
                - workers: 工作进程数，默认 1
                - title: API标题，默认 "WordPress REST API"
                - description: API描述
                - version: API版本，默认 "1.0.0"
                - docs_url: 文档URL，默认 "/docs"
                - redoc_url: ReDoc URL，默认 "/redoc"
                - openapi_url: OpenAPI URL，默认 "/openapi.json"
                - cors_origins: CORS允许的源，默认 ["*"]
                - middleware: 自定义中间件列表
                - wordpress_config: WordPress配置
        """
        if config:
            self.configure(config)
        
        # 创建FastAPI应用
        self.app = FastAPI(
            title=self.get_config("title", "WordPress REST API"),
            description=self.get_config("description", "基于wp-python的WordPress REST API服务"),
            version=self.get_config("version", "1.0.0"),
            docs_url=self.get_config("docs_url", "/docs"),
            redoc_url=self.get_config("redoc_url", "/redoc"),
            openapi_url=self.get_config("openapi_url", "/openapi.json")
        )
        
        # 添加WordPress中间件
        wordpress_middleware = WordPressMiddleware(
            wordpress_config=self.get_config("wordpress_config", {})
        )
        self.app.add_middleware(
            type(wordpress_middleware),
            **wordpress_middleware.get_middleware_kwargs()
        )
        
        # 添加CORS中间件
        cors_origins = self.get_config("cors_origins", ["*"])
        if cors_origins:
            from fastapi.middleware.cors import CORSMiddleware
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # 添加自定义中间件
        custom_middleware = self.get_config("middleware", [])
        for middleware in custom_middleware:
            self.app.add_middleware(middleware)
        
        # 创建WordPress路由器
        wp_router = WordPressRouter(
            wordpress_config=self.get_config("wordpress_config", {})
        )
        
        # 注册路由
        self.app.include_router(wp_router.get_router(), prefix="/api/v1")
        
        # 创建服务器
        self.server = FastAPIServer(
            app=self.app,
            host=self.get_config("host", "0.0.0.0"),
            port=self.get_config("port", 8000),
            debug=self.get_config("debug", False),
            reload=self.get_config("reload", False),
            workers=self.get_config("workers", 1)
        )
        
        self.logger.success("FastAPI插件初始化完成")
    
    def start(self) -> None:
        """启动FastAPI服务器"""
        if not self.server:
            raise RuntimeError("插件未初始化，请先调用 initialize()")
        
        if not self.enabled:
            self.enable()
        
        self.logger.info("启动FastAPI服务器...")
        
        # 在开发模式下使用异步启动
        if self.get_config("debug", False):
            self._start_async()
        else:
            # 生产模式使用Gunicorn
            self.server.start_production()
    
    def _start_async(self) -> None:
        """异步启动服务器（开发模式）"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # 如果事件循环已在运行，创建任务
            self._server_task = loop.create_task(self.server.start_async())
        else:
            # 否则直接运行
            loop.run_until_complete(self.server.start_async())
    
    def stop(self) -> None:
        """停止FastAPI服务器"""
        if self.server:
            self.logger.info("停止FastAPI服务器...")
            
            if self._server_task:
                self._server_task.cancel()
                self._server_task = None
            
            self.server.stop()
            self.logger.success("FastAPI服务器已停止")
    
    def get_app(self) -> Optional[FastAPI]:
        """
        获取FastAPI应用实例
        
        返回:
            FastAPI应用实例
        """
        return self.app
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        获取服务器信息
        
        返回:
            服务器信息字典
        """
        if not self.server:
            return {"status": "未初始化"}
        
        return {
            "status": "运行中" if self.enabled else "已停止",
            "host": self.get_config("host", "0.0.0.0"),
            "port": self.get_config("port", 8000),
            "debug": self.get_config("debug", False),
            "reload": self.get_config("reload", False),
            "workers": self.get_config("workers", 1),
            "docs_url": f"http://{self.get_config('host', '0.0.0.0')}:{self.get_config('port', 8000)}{self.get_config('docs_url', '/docs')}",
            "api_url": f"http://{self.get_config('host', '0.0.0.0')}:{self.get_config('port', 8000)}/api/v1"
        }
    
    def add_custom_route(self, router) -> None:
        """
        添加自定义路由
        
        参数:
            router: FastAPI路由器
        """
        if self.app:
            self.app.include_router(router)
            self.logger.info("已添加自定义路由")
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件详细信息"""
        info = super().get_info()
        info.update({
            "server_info": self.get_server_info(),
            "features": [
                "FastAPI Web框架",
                "自动WordPress API路由", 
                "CORS支持",
                "中间件系统",
                "Gunicorn + Uvicorn部署",
                "热重载开发模式",
                "自动API文档"
            ]
        })
        return info