"""
FastAPI 中间件

提供WordPress相关的中间件功能，包括认证、日志、错误处理等。
"""

import time
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from ...utils.logger import get_logger
from ...utils.config import get_config


class WordPressMiddleware(BaseHTTPMiddleware):
    """
    WordPress中间件
    
    提供WordPress相关的请求处理功能：
    - 请求日志记录
    - 性能监控
    - 错误处理
    - WordPress配置注入
    """
    
    def __init__(self, app=None, wordpress_config: Optional[Dict[str, Any]] = None):
        """
        初始化中间件
        
        参数:
            app: FastAPI应用实例
            wordpress_config: WordPress配置
        """
        super().__init__(app)
        self.logger = get_logger("wordpress_middleware")
        self.wordpress_config = wordpress_config or {}
        self.wp_config = get_config()
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        处理请求
        
        参数:
            request: 请求对象
            call_next: 下一个处理器
            
        返回:
            响应对象
        """
        start_time = time.time()
        
        # 记录请求开始
        self.logger.debug(f"🔄 {request.method} {request.url.path} - 开始处理")
        
        # 在请求状态中注入WordPress配置
        request.state.wordpress_config = self.wp_config
        request.state.custom_config = self.wordpress_config
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 添加响应头
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Powered-By"] = "wp-python FastAPI Plugin"
            
            # 记录请求完成
            status_emoji = "✅" if response.status_code < 400 else "❌"
            self.logger.info(
                f"{status_emoji} {request.method} {request.url.path} "
                f"- {response.status_code} - {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # 处理异常
            process_time = time.time() - start_time
            
            self.logger.error(
                f"💥 {request.method} {request.url.path} "
                f"- 错误: {str(e)} - {process_time:.3f}s"
            )
            
            # 重新抛出异常，让FastAPI的异常处理器处理
            raise
    
    def get_middleware_kwargs(self) -> Dict[str, Any]:
        """
        获取中间件参数
        
        返回:
            中间件参数字典
        """
        return {
            "wordpress_config": self.wordpress_config
        }


class CacheMiddleware(BaseHTTPMiddleware):
    """
    缓存中间件
    
    提供简单的内存缓存功能。
    """
    
    def __init__(self, app=None, cache_ttl: int = 300):
        """
        初始化缓存中间件
        
        参数:
            app: FastAPI应用实例
            cache_ttl: 缓存TTL（秒）
        """
        super().__init__(app)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = cache_ttl
        self.logger = get_logger("cache_middleware")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """处理缓存逻辑"""
        # 只缓存GET请求
        if request.method != "GET":
            return await call_next(request)
        
        cache_key = str(request.url)
        current_time = time.time()
        
        # 检查缓存
        if cache_key in self.cache:
            cache_data = self.cache[cache_key]
            if current_time - cache_data["timestamp"] < self.cache_ttl:
                self.logger.debug(f"🎯 缓存命中: {cache_key}")
                
                # 从缓存返回响应
                response = Response(
                    content=cache_data["content"],
                    status_code=cache_data["status_code"],
                    headers=cache_data["headers"]
                )
                response.headers["X-Cache"] = "HIT"
                return response
        
        # 处理请求
        response = await call_next(request)
        
        # 缓存成功响应
        if response.status_code == 200:
            self.cache[cache_key] = {
                "content": response.body,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "timestamp": current_time
            }
            response.headers["X-Cache"] = "MISS"
            self.logger.debug(f"💾 已缓存: {cache_key}")
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    速率限制中间件
    
    提供简单的速率限制功能。
    """
    
    def __init__(self, app=None, max_requests: int = 100, window_seconds: int = 60):
        """
        初始化速率限制中间件
        
        参数:
            app: FastAPI应用实例
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口（秒）
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
        self.logger = get_logger("rate_limit_middleware")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """处理速率限制逻辑"""
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 清理过期记录
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < self.window_seconds
            ]
        else:
            self.requests[client_ip] = []
        
        # 检查速率限制
        if len(self.requests[client_ip]) >= self.max_requests:
            self.logger.warning(f"🚫 速率限制: {client_ip} - {len(self.requests[client_ip])} 请求")
            
            from fastapi import HTTPException
            raise HTTPException(
                status_code=429,
                detail="请求过于频繁，请稍后再试"
            )
        
        # 记录请求
        self.requests[client_ip].append(current_time)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加速率限制头
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.max_requests - len(self.requests[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + self.window_seconds)
        )
        
        return response