"""
WordPress REST API 主客户端类

这是WordPress REST API Python客户端的主入口点，
提供了对所有WordPress REST API功能的统一访问接口。
"""

from typing import Optional, Dict, Any
from urllib.parse import urlparse

from .core.client import WordPressClient, AsyncWordPressClient, AuthConfig
from .core.exceptions import WordPressError, ValidationError
from .service.posts import PostService, AsyncPostService
from .service.pages import PageService, AsyncPageService
from .service.categories import CategoryService, AsyncCategoryService
from .service.tags import TagService, AsyncTagService
from .service.users import UserService, AsyncUserService
from .service.media import MediaService, AsyncMediaService
from .service.comments import CommentService, AsyncCommentService


class WordPress:
    """
    WordPress REST API 主客户端类
    
    这是访问WordPress REST API的主要接口，提供了对所有
    WordPress内容类型的统一访问方法。
    
    使用示例:
        # 基础认证
        wp = WordPress('https://your-site.com', username='用户名', password='密码')
        
        # 应用程序密码认证
        wp = WordPress('https://your-site.com', username='用户名', app_password='应用程序密码')
        
        # JWT令牌认证
        wp = WordPress('https://your-site.com', jwt_token='your-jwt-token')
        
        # 无认证（只读访问）
        wp = WordPress('https://your-site.com')
    """
    
    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        app_password: Optional[str] = None,
        jwt_token: Optional[str] = None,
        wp_nonce: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        user_agent: str = "wp-python/0.2.0"
    ):
        """
        初始化WordPress客户端
        
        参数:
            base_url: WordPress站点URL
            username: 用户名（用于基础认证或应用程序密码）
            password: 密码（用于基础认证）
            app_password: 应用程序密码（推荐用于生产环境）
            jwt_token: JWT令牌（需要JWT插件支持）
            wp_nonce: WordPress nonce（用于Cookie认证）
            cookies: Cookie字典（用于Cookie认证）
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证SSL证书
            user_agent: 用户代理字符串
            
        异常:
            ValidationError: 参数验证失败
        """
        # 验证URL格式
        self.base_url = self._validate_url(base_url)
        
        # 创建认证配置
        auth = AuthConfig(
            username=username,
            password=password,
            app_password=app_password,
            jwt_token=jwt_token,
            wp_nonce=wp_nonce,
            cookies=cookies
        )
        
        # 创建HTTP客户端
        self.client = WordPressClient(
            base_url=self.base_url,
            auth=auth,
            timeout=timeout,
            verify_ssl=verify_ssl,
            user_agent=user_agent
        )
        
        # 初始化服务
        self._init_services()
    
    def _validate_url(self, url: str) -> str:
        """
        验证和标准化URL
        
        参数:
            url: 输入的URL
            
        返回:
            标准化的URL
            
        异常:
            ValidationError: URL格式无效
        """
        if not url:
            raise ValidationError("URL不能为空")
        
        # 如果没有协议，默认使用https
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 验证URL格式
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValidationError(f"无效的URL格式: {url}")
        except Exception as e:
            raise ValidationError(f"URL解析失败: {str(e)}")
        
        return url.rstrip('/')
    
    def _init_services(self) -> None:
        """初始化所有服务"""
        self.posts = PostService(self.client)
        self.pages = PageService(self.client)
        self.categories = CategoryService(self.client)
        self.tags = TagService(self.client)
        self.users = UserService(self.client)
        self.media = MediaService(self.client)
        self.comments = CommentService(self.client)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        测试与WordPress站点的连接
        
        返回:
            站点信息和连接状态
            
        异常:
            WordPressError: 连接失败
        """
        try:
            # 获取API根信息
            response = self.client.get("")
            return {
                "status": "connected",
                "site_info": response,
                "api_url": self.client.api_url
            }
        except Exception as e:
            raise WordPressError(f"连接测试失败: {str(e)}")
    
    def get_site_info(self) -> Dict[str, Any]:
        """
        获取WordPress站点信息
        
        返回:
            站点基本信息
        """
        try:
            # 尝试获取站点设置信息（需要认证）
            settings = self.client.get("settings")
            return {
                "name": settings.get("title", "未知"),
                "description": settings.get("description", "未知"),
                "url": settings.get("url", "未知"),
                "admin_email": settings.get("admin_email", "未知"),
                "timezone": settings.get("timezone_string", "未知"),
                "date_format": settings.get("date_format", "未知"),
                "time_format": settings.get("time_format", "未知"),
                "language": settings.get("language", "未知")
            }
        except Exception:
            # 如果无法获取设置，返回API根信息
            api_info = self.client.get("")
            return {
                "name": "未知（需要认证获取站点设置）",
                "description": "未知（需要认证获取站点设置）", 
                "url": self.base_url,
                "namespace": api_info.get("namespace", "未知"),
                "routes_count": len(api_info.get("routes", {})),
                "api_info": "可访问API根端点"
            }
    
    def close(self) -> None:
        """关闭客户端连接"""
        self.client.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"WordPress(base_url='{self.base_url}')"


class AsyncWordPress:
    """
    WordPress REST API 异步客户端类
    
    提供异步访问WordPress REST API的功能，适用于
    高并发场景和异步应用程序。
    
    使用示例:
        async with AsyncWordPress('https://your-site.com') as wp:
            posts = await wp.posts.list()
            # 处理文章...
    """
    
    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        app_password: Optional[str] = None,
        jwt_token: Optional[str] = None,
        wp_nonce: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        user_agent: str = "wp-python/0.2.0"
    ):
        """
        初始化异步WordPress客户端
        
        参数与同步版本相同
        """
        # 验证URL格式
        self.base_url = self._validate_url(base_url)
        
        # 创建认证配置
        auth = AuthConfig(
            username=username,
            password=password,
            app_password=app_password,
            jwt_token=jwt_token,
            wp_nonce=wp_nonce,
            cookies=cookies
        )
        
        # 创建异步HTTP客户端
        self.client = AsyncWordPressClient(
            base_url=self.base_url,
            auth=auth,
            timeout=timeout,
            verify_ssl=verify_ssl,
            user_agent=user_agent
        )
        
        # 初始化异步服务
        self._init_services()
    
    def _validate_url(self, url: str) -> str:
        """验证和标准化URL（与同步版本相同）"""
        if not url:
            raise ValidationError("URL不能为空")
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValidationError(f"无效的URL格式: {url}")
        except Exception as e:
            raise ValidationError(f"URL解析失败: {str(e)}")
        
        return url.rstrip('/')
    
    def _init_services(self) -> None:
        """初始化所有异步服务"""
        self.posts = AsyncPostService(self.client)
        self.pages = AsyncPageService(self.client)
        self.categories = AsyncCategoryService(self.client)
        self.tags = AsyncTagService(self.client)
        self.users = AsyncUserService(self.client)
        self.media = AsyncMediaService(self.client)
        self.comments = AsyncCommentService(self.client)
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        异步测试与WordPress站点的连接
        
        返回:
            站点信息和连接状态
        """
        try:
            response = await self.client.get("")
            return {
                "status": "connected",
                "site_info": response,
                "api_url": self.client.api_url
            }
        except Exception as e:
            raise WordPressError(f"连接测试失败: {str(e)}")
    
    async def get_site_info(self) -> Dict[str, Any]:
        """
        异步获取WordPress站点信息
        
        返回:
            站点基本信息
        """
        try:
            # 尝试获取站点设置信息（需要认证）
            settings = await self.client.get("settings")
            return {
                "name": settings.get("title", "未知"),
                "description": settings.get("description", "未知"),
                "url": settings.get("url", "未知"),
                "admin_email": settings.get("admin_email", "未知"),
                "timezone": settings.get("timezone_string", "未知"),
                "date_format": settings.get("date_format", "未知"),
                "time_format": settings.get("time_format", "未知"),
                "language": settings.get("language", "未知")
            }
        except Exception:
            # 如果无法获取设置，返回API根信息
            api_info = await self.client.get("")
            return {
                "name": "未知（需要认证获取站点设置）",
                "description": "未知（需要认证获取站点设置）",
                "url": self.base_url,
                "namespace": api_info.get("namespace", "未知"),
                "routes_count": len(api_info.get("routes", {})),
                "api_info": "可访问API根端点"
            }
    
    async def close(self) -> None:
        """关闭异步客户端连接"""
        await self.client.close()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"AsyncWordPress(base_url='{self.base_url}')"