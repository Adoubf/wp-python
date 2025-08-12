"""
WordPress REST API 异常类定义

定义了所有可能的API错误和异常类型，
基于WordPress官方文档的错误响应规范。
"""

from typing import Optional, Dict, Any


class WordPressError(Exception):
    """WordPress API 基础异常类"""
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None
    ):
        """
        初始化WordPress异常
        
        参数:
            message: 错误消息
            code: WordPress错误代码
            status_code: HTTP状态码
            data: 额外的错误数据
            endpoint: 出错的API端点
            method: HTTP方法
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.data = data or {}
        self.endpoint = endpoint
        self.method = method
    
    def __str__(self) -> str:
        """返回格式化的错误信息"""
        parts = []
        
        if self.code:
            parts.append(f"[{self.code}]")
        
        if self.status_code:
            parts.append(f"HTTP {self.status_code}")
        
        if self.method and self.endpoint:
            parts.append(f"{self.method} {self.endpoint}")
        
        parts.append(self.message)
        
        return " ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'code': self.code,
            'status_code': self.status_code,
            'endpoint': self.endpoint,
            'method': self.method,
            'data': self.data
        }


class AuthenticationError(WordPressError):
    """认证相关错误
    
    当API请求需要认证但认证失败时抛出，
    包括无效的用户名/密码、过期的令牌等。
    """
    pass


class PermissionError(WordPressError):
    """权限不足错误
    
    当用户已认证但没有执行特定操作的权限时抛出。
    """
    pass


class NotFoundError(WordPressError):
    """资源未找到错误
    
    当请求的资源（文章、页面、用户等）不存在时抛出。
    """
    pass


class ValidationError(WordPressError):
    """数据验证错误
    
    当提交的数据不符合WordPress API要求时抛出，
    包括必填字段缺失、数据格式错误等。
    """
    pass


class RateLimitError(WordPressError):
    """请求频率限制错误
    
    当API请求超过频率限制时抛出。
    """
    pass


class ServerError(WordPressError):
    """服务器内部错误
    
    当WordPress服务器发生内部错误时抛出。
    """
    pass


class NetworkError(WordPressError):
    """网络连接错误
    
    当无法连接到WordPress站点时抛出。
    """
    pass


def create_exception_from_response(
    status_code: int,
    response_data: Dict[str, Any]
) -> WordPressError:
    """
    根据API响应创建相应的异常对象
    
    参数:
        status_code: HTTP状态码
        response_data: API响应数据
        
    返回:
        相应的异常对象
    """
    # 提取错误信息
    message = response_data.get('message', '未知错误')
    code = response_data.get('code', None)
    data = response_data.get('data', {})
    
    # 根据状态码和错误代码选择异常类型
    if status_code == 401:
        return AuthenticationError(message, code, status_code, data)
    elif status_code == 403:
        return PermissionError(message, code, status_code, data)
    elif status_code == 404:
        return NotFoundError(message, code, status_code, data)
    elif status_code == 400:
        return ValidationError(message, code, status_code, data)
    elif status_code == 429:
        return RateLimitError(message, code, status_code, data)
    elif status_code >= 500:
        return ServerError(message, code, status_code, data)
    else:
        return WordPressError(message, code, status_code, data)