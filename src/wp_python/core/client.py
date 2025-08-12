"""
WordPress REST API HTTP客户端

提供同步和异步的HTTP请求功能，
支持多种认证方式和错误处理。
"""

from typing import Optional, Dict, Any
from urllib.parse import urljoin
import json
import base64

import requests
import httpx
from pydantic import BaseModel

from .exceptions import (
    WordPressError,
    NetworkError,
    create_exception_from_response
)


class AuthConfig(BaseModel):
    """认证配置模型"""
    
    # 基础认证
    username: Optional[str] = None
    password: Optional[str] = None
    
    # JWT令牌认证
    jwt_token: Optional[str] = None
    
    # 应用程序密码认证
    app_password: Optional[str] = None
    
    # Cookie认证
    wp_nonce: Optional[str] = None
    cookies: Optional[Dict[str, str]] = None


class WordPressClient:
    """WordPress REST API 同步客户端"""
    
    def __init__(
        self,
        base_url: str,
        auth: Optional[AuthConfig] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        user_agent: str = "wp-python/0.2.0"
    ):
        """
        初始化WordPress客户端
        
        参数:
            base_url: WordPress站点URL
            auth: 认证配置
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证SSL证书
            user_agent: 用户代理字符串
        """
        self.base_url = self._normalize_url(base_url)
        self.api_url = urljoin(self.base_url, '/wp-json/wp/v2/')
        self.auth = auth or AuthConfig()
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # 创建requests会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # 设置认证
        self._setup_auth()
    
    def _normalize_url(self, url: str) -> str:
        """标准化URL格式"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
    
    def _setup_auth(self) -> None:
        """设置认证方式"""
        if self.auth.username and (self.auth.password or self.auth.app_password):
            # 基础认证或应用程序密码
            password = self.auth.app_password or self.auth.password
            self.session.auth = (self.auth.username, password)
        
        elif self.auth.jwt_token:
            # JWT令牌认证
            self.session.headers['Authorization'] = f'Bearer {self.auth.jwt_token}'
        
        elif self.auth.wp_nonce:
            # Cookie认证
            self.session.headers['X-WP-Nonce'] = self.auth.wp_nonce
            if self.auth.cookies:
                self.session.cookies.update(self.auth.cookies)
    
    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        参数:
            method: HTTP方法
            endpoint: API端点
            params: URL参数
            data: 请求数据
            files: 文件上传
            
        返回:
            API响应数据
            
        异常:
            WordPressError: API错误
            NetworkError: 网络错误
        """
        url = urljoin(self.api_url, endpoint.lstrip('/'))
        
        try:
            # 处理文件上传
            if files:
                # 文件上传时不设置Content-Type，让requests自动设置
                headers = {k: v for k, v in self.session.headers.items() 
                          if k.lower() != 'content-type'}
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
            else:
                # 普通请求
                json_data = json.dumps(data) if data else None
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=json_data,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
            
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            raise NetworkError("请求超时")
        except requests.exceptions.ConnectionError:
            raise NetworkError("无法连接到WordPress站点")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"网络请求失败: {str(e)}")
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        处理HTTP响应
        
        参数:
            response: requests响应对象
            
        返回:
            解析后的响应数据
            
        异常:
            WordPressError: API错误
        """
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            # 如果响应不是JSON格式
            if response.status_code >= 400:
                raise WordPressError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
            response_data = {"message": response.text}
        
        # 检查HTTP状态码
        if response.status_code >= 400:
            raise create_exception_from_response(response.status_code, response_data)
        
        return response_data
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET请求"""
        return self.request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
             files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POST请求"""
        return self.request('POST', endpoint, data=data, files=files)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """PUT请求"""
        return self.request('PUT', endpoint, data=data)
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """PATCH请求"""
        return self.request('PATCH', endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE请求"""
        return self.request('DELETE', endpoint)
    
    def close(self) -> None:
        """关闭客户端会话"""
        self.session.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


class AsyncWordPressClient:
    """WordPress REST API 异步客户端"""
    
    def __init__(
        self,
        base_url: str,
        auth: Optional[AuthConfig] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        user_agent: str = "wp-python/0.2.0"
    ):
        """
        初始化异步WordPress客户端
        
        参数:
            base_url: WordPress站点URL
            auth: 认证配置
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证SSL证书
            user_agent: 用户代理字符串
        """
        self.base_url = self._normalize_url(base_url)
        self.api_url = urljoin(self.base_url, '/wp-json/wp/v2/')
        self.auth = auth or AuthConfig()
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # 设置请求头
        self.headers = {
            'User-Agent': user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # 设置认证
        self._setup_auth()
        
        # httpx客户端将在需要时创建
        self._client: Optional[httpx.AsyncClient] = None
    
    def _normalize_url(self, url: str) -> str:
        """标准化URL格式"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
    
    def _setup_auth(self) -> None:
        """设置认证方式"""
        if self.auth.username and (self.auth.password or self.auth.app_password):
            # 基础认证或应用程序密码
            password = self.auth.app_password or self.auth.password
            credentials = base64.b64encode(f"{self.auth.username}:{password}".encode()).decode()
            self.headers['Authorization'] = f'Basic {credentials}'
        
        elif self.auth.jwt_token:
            # JWT令牌认证
            self.headers['Authorization'] = f'Bearer {self.auth.jwt_token}'
        
        elif self.auth.wp_nonce:
            # Cookie认证
            self.headers['X-WP-Nonce'] = self.auth.wp_nonce
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取或创建httpx客户端"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                verify=self.verify_ssl,
                headers=self.headers
            )
            
            # 设置Cookie认证
            if self.auth.cookies:
                for name, value in self.auth.cookies.items():
                    self._client.cookies.set(name, value)
        
        return self._client
    
    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送异步HTTP请求
        
        参数:
            method: HTTP方法
            endpoint: API端点
            params: URL参数
            data: 请求数据
            files: 文件上传
            
        返回:
            API响应数据
            
        异常:
            WordPressError: API错误
            NetworkError: 网络错误
        """
        url = urljoin(self.api_url, endpoint.lstrip('/'))
        client = await self._get_client()
        
        try:
            # 处理文件上传
            if files:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    files=files
                )
            else:
                # 普通请求
                json_data = data if data else None
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data
                )
            
            return await self._handle_response(response)
            
        except httpx.TimeoutException:
            raise NetworkError("请求超时")
        except httpx.ConnectError:
            raise NetworkError("无法连接到WordPress站点")
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}")
    
    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        处理HTTP响应
        
        参数:
            response: httpx响应对象
            
        返回:
            解析后的响应数据
            
        异常:
            WordPressError: API错误
        """
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            # 如果响应不是JSON格式
            if response.status_code >= 400:
                raise WordPressError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
            response_data = {"message": response.text}
        
        # 检查HTTP状态码
        if response.status_code >= 400:
            raise create_exception_from_response(response.status_code, response_data)
        
        return response_data
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """异步GET请求"""
        return await self.request('GET', endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
                   files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """异步POST请求"""
        return await self.request('POST', endpoint, data=data, files=files)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """异步PUT请求"""
        return await self.request('PUT', endpoint, data=data)
    
    async def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """异步PATCH请求"""
        return await self.request('PATCH', endpoint, data=data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """异步DELETE请求"""
        return await self.request('DELETE', endpoint)
    
    async def close(self) -> None:
        """关闭异步客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()