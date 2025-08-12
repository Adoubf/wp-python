"""
FastAPI 服务器管理

提供FastAPI服务器的启动、停止和管理功能，支持开发和生产环境。
"""

import asyncio
import signal
import sys
from typing import Optional
import uvicorn
import gunicorn.app.base
from fastapi import FastAPI

from ...utils.logger import get_logger


class GunicornApplication(gunicorn.app.base.BaseApplication):
    """Gunicorn应用包装器"""
    
    def __init__(self, app: FastAPI, options: dict = None):
        """
        初始化Gunicorn应用
        
        参数:
            app: FastAPI应用实例
            options: Gunicorn配置选项
        """
        self.options = options or {}
        self.application = app
        super().__init__()
    
    def load_config(self):
        """加载配置"""
        config = {
            key: value for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)
    
    def load(self):
        """加载应用"""
        return self.application


class FastAPIServer:
    """
    FastAPI服务器管理器
    
    提供开发和生产环境的服务器启动管理。
    """
    def __init__(
        self,
        app: FastAPI,
        host: str = "0.0.0.0",
        port: int = 8000,
        debug: bool = False,
        reload: bool = False,
        workers: int = 1
    ):
        """
        初始化服务器
        
        参数:
            app: FastAPI应用实例
            host: 服务器主机
            port: 服务器端口
            debug: 调试模式
            reload: 热重载
            workers: 工作进程数
        """
        self.app = app
        self.host = host
        self.port = port
        self.debug = debug
        self.reload = reload
        self.workers = workers
        self.logger = get_logger("fastapi_server")
        self._server: Optional[uvicorn.Server] = None
        self._gunicorn_app: Optional[GunicornApplication] = None
    
    async def start_async(self) -> None:
        """异步启动服务器（开发模式）"""
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="debug" if self.debug else "info",
            reload=self.reload,
            access_log=True
        )
        
        self._server = uvicorn.Server(config)
        
        self.logger.success(f"🚀 FastAPI服务器启动成功")
        self.logger.info(f"📍 服务地址: http://{self.host}:{self.port}")
        self.logger.info(f"📚 API文档: http://{self.host}:{self.port}/docs")
        self.logger.info(f"📖 ReDoc文档: http://{self.host}:{self.port}/redoc")
        
        # 设置信号处理
        self._setup_signal_handlers()
        
        try:
            await self._server.serve()
        except asyncio.CancelledError:
            self.logger.info("服务器被取消")
        except Exception as e:
            self.logger.error(f"服务器运行错误: {e}")
    
    def start_production(self) -> None:
        """启动生产服务器（使用Gunicorn）"""
        options = {
            'bind': f'{self.host}:{self.port}',
            'workers': self.workers,
            'worker_class': 'uvicorn.workers.UvicornWorker',
            'worker_connections': 1000,
            'max_requests': 1000,
            'max_requests_jitter': 100,
            'preload_app': True,
            'keepalive': 2,
            'timeout': 30,
            'graceful_timeout': 30,
            'access_log': True,
            'error_log': '-',
            'log_level': 'debug' if self.debug else 'info'
        }
        
        self._gunicorn_app = GunicornApplication(self.app, options)
        
        self.logger.success(f"🚀 FastAPI生产服务器启动成功")
        self.logger.info(f"📍 服务地址: http://{self.host}:{self.port}")
        self.logger.info(f"👥 工作进程数: {self.workers}")
        self.logger.info(f"📚 API文档: http://{self.host}:{self.port}/docs")
        
        try:
            self._gunicorn_app.run()
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，正在停止服务器...")
        except Exception as e:
            self.logger.error(f"生产服务器运行错误: {e}")
    
    def start_development(self) -> None:
        """启动开发服务器（使用Uvicorn）"""
        self.logger.info("启动开发服务器...")
        
        try:
            uvicorn.run(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="debug" if self.debug else "info",
                reload=self.reload,
                access_log=True
            )
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，正在停止服务器...")
        except Exception as e:
            self.logger.error(f"开发服务器运行错误: {e}")
    
    def stop(self) -> None:
        """停止服务器"""
        if self._server:
            self.logger.info("正在停止异步服务器...")
            self._server.should_exit = True
        
        if self._gunicorn_app:
            self.logger.info("正在停止Gunicorn服务器...")
            # Gunicorn会通过信号处理自动停止
        
        self.logger.success("服务器已停止")
    
    def _setup_signal_handlers(self) -> None:
        """设置信号处理器"""
        if sys.platform != "win32":
            # Unix系统信号处理
            def signal_handler(signum, frame):
                self.logger.info(f"收到信号 {signum}，正在优雅关闭...")
                if self._server:
                    self._server.should_exit = True
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
    
    def get_status(self) -> dict:
        """
        获取服务器状态
        
        返回:
            服务器状态信息
        """
        return {
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "reload": self.reload,
            "workers": self.workers,
            "running": self._server is not None or self._gunicorn_app is not None,
            "server_type": "uvicorn" if self._server else "gunicorn" if self._gunicorn_app else "none"
        }