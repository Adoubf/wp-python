"""
WordPress 用户服务

提供用户的CRUD操作，基于WordPress官方REST API文档。
用户管理需要适当的权限，某些操作只有管理员才能执行。
"""

from typing import List, Optional, Dict, Any

from ..core.models import User
from ..core.client import WordPressClient, AsyncWordPressClient


class UserService:
    """用户服务类 - 同步版本"""
    
    def __init__(self, client: WordPressClient):
        """
        初始化用户服务
        
        参数:
            client: WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "users"
    
    def list(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        exclude: Optional[List[int]] = None,
        include: Optional[List[int]] = None,
        offset: Optional[int] = None,
        order: str = "asc",
        orderby: str = "name",
        slug: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        who: Optional[str] = None,
        has_published_posts: Optional[List[str]] = None,
        context: str = "view",
        **kwargs
    ) -> List[User]:
        """
        获取用户列表
        
        参数:
            page: 页码，从1开始
            per_page: 每页用户数量，最大100
            search: 搜索关键词
            exclude: 排除的用户ID列表
            include: 包含的用户ID列表
            offset: 偏移量
            order: 排序方向 (asc/desc)
            orderby: 排序字段 (id/include/name/registered_date/slug/include_slugs/email/url)
            slug: 用户别名列表
            roles: 用户角色列表
            capabilities: 用户权限列表
            who: 特定用户组 (authors)
            has_published_posts: 已发布文章的文章类型列表
            context: 响应上下文 (view/embed/edit)
            **kwargs: 其他查询参数
            
        返回:
            用户对象列表
        """
        # 构建查询参数
        params = {
            "page": page,
            "per_page": per_page,
            "context": context,
            "order": order,
            "orderby": orderby
        }
        
        # 添加可选参数
        if search:
            params["search"] = search
        if exclude:
            params["exclude"] = ",".join(map(str, exclude))
        if include:
            params["include"] = ",".join(map(str, include))
        if offset is not None:
            params["offset"] = offset
        if slug:
            params["slug"] = ",".join(slug)
        if roles:
            params["roles"] = ",".join(roles)
        if capabilities:
            params["capabilities"] = ",".join(capabilities)
        if who:
            params["who"] = who
        if has_published_posts:
            params["has_published_posts"] = ",".join(has_published_posts)
        
        # 添加额外参数
        params.update(kwargs)
        
        # 发送请求
        response = self.client.get(self.endpoint, params=params)
        
        # 转换为User对象列表
        return [User.from_api_response(user_data) for user_data in response]
    
    def get(self, user_id: int, context: str = "view") -> User:
        """
        获取单个用户
        
        参数:
            user_id: 用户ID
            context: 响应上下文 (view/embed/edit)
            
        返回:
            用户对象
            
        异常:
            NotFoundError: 用户不存在
        """
        params = {"context": context}
        response = self.client.get(f"{self.endpoint}/{user_id}", params=params)
        return User.from_api_response(response)
    
    def get_me(self, context: str = "view") -> User:
        """
        获取当前用户信息
        
        参数:
            context: 响应上下文 (view/embed/edit)
            
        返回:
            当前用户对象
            
        异常:
            AuthenticationError: 未认证
        """
        params = {"context": context}
        response = self.client.get(f"{self.endpoint}/me", params=params)
        return User.from_api_response(response)
    
    def create(
        self,
        username: str,
        email: str,
        password: str,
        name: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        url: Optional[str] = None,
        description: Optional[str] = None,
        locale: Optional[str] = None,
        nickname: Optional[str] = None,
        slug: Optional[str] = None,
        roles: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> User:
        """
        创建新用户
        
        参数:
            username: 用户名
            email: 邮箱地址
            password: 密码
            name: 显示名称
            first_name: 名字
            last_name: 姓氏
            url: 网站URL
            description: 用户描述
            locale: 用户语言
            nickname: 昵称
            slug: 用户别名
            roles: 用户角色列表
            meta: 自定义字段
            **kwargs: 其他字段
            
        返回:
            创建的用户对象
            
        异常:
            ValidationError: 数据验证失败
            PermissionError: 权限不足
        """
        # 构建请求数据
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        # 添加可选字段
        if name is not None:
            data["name"] = name
        if first_name is not None:
            data["first_name"] = first_name
        if last_name is not None:
            data["last_name"] = last_name
        if url is not None:
            data["url"] = url
        if description is not None:
            data["description"] = description
        if locale is not None:
            data["locale"] = locale
        if nickname is not None:
            data["nickname"] = nickname
        if slug is not None:
            data["slug"] = slug
        if roles is not None:
            data["roles"] = roles
        if meta is not None:
            data["meta"] = meta
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(self.endpoint, data=data)
        return User.from_api_response(response)
    
    def update(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        name: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        url: Optional[str] = None,
        description: Optional[str] = None,
        locale: Optional[str] = None,
        nickname: Optional[str] = None,
        slug: Optional[str] = None,
        roles: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> User:
        """
        更新用户
        
        参数:
            user_id: 用户ID
            其他参数与create方法相同（除了password不是必需的）
            
        返回:
            更新后的用户对象
            
        异常:
            NotFoundError: 用户不存在
            ValidationError: 数据验证失败
            PermissionError: 权限不足
        """
        # 构建请求数据（只包含非None的字段）
        data = {}
        
        if username is not None:
            data["username"] = username
        if email is not None:
            data["email"] = email
        if password is not None:
            data["password"] = password
        if name is not None:
            data["name"] = name
        if first_name is not None:
            data["first_name"] = first_name
        if last_name is not None:
            data["last_name"] = last_name
        if url is not None:
            data["url"] = url
        if description is not None:
            data["description"] = description
        if locale is not None:
            data["locale"] = locale
        if nickname is not None:
            data["nickname"] = nickname
        if slug is not None:
            data["slug"] = slug
        if roles is not None:
            data["roles"] = roles
        if meta is not None:
            data["meta"] = meta
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(f"{self.endpoint}/{user_id}", data=data)
        return User(**response)
    
    def update_me(self, **kwargs) -> User:
        """
        更新当前用户信息
        
        参数:
            **kwargs: 更新字段（与update方法相同）
            
        返回:
            更新后的当前用户对象
        """
        # 构建请求数据
        data = {}
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        
        # 发送请求
        response = self.client.post(f"{self.endpoint}/me", data=data)
        return User(**response)
    
    def delete(self, user_id: int, force: bool = False, reassign: Optional[int] = None) -> Dict[str, Any]:
        """
        删除用户
        
        参数:
            user_id: 用户ID
            force: 是否强制删除
            reassign: 将用户的文章重新分配给指定用户ID
            
        返回:
            删除操作的结果
            
        异常:
            NotFoundError: 用户不存在
            PermissionError: 权限不足
        """
        params = {}
        if force:
            params["force"] = True
        if reassign is not None:
            params["reassign"] = reassign
        
        return self.client.delete(f"{self.endpoint}/{user_id}")


class AsyncUserService:
    """用户服务类 - 异步版本"""
    
    def __init__(self, client: AsyncWordPressClient):
        """
        初始化异步用户服务
        
        参数:
            client: 异步WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "users"
    
    async def list(self, **kwargs) -> List[User]:
        """异步获取用户列表"""
        params = self._build_params(**kwargs)
        response = await self.client.get(self.endpoint, params=params)
        return [User(**user_data) for user_data in response]
    
    async def get(self, user_id: int, context: str = "view") -> User:
        """异步获取单个用户"""
        params = {"context": context}
        response = await self.client.get(f"{self.endpoint}/{user_id}", params=params)
        return User(**response)
    
    async def get_me(self, context: str = "view") -> User:
        """异步获取当前用户信息"""
        params = {"context": context}
        response = await self.client.get(f"{self.endpoint}/me", params=params)
        return User(**response)
    
    async def create(self, **kwargs) -> User:
        """异步创建用户"""
        data = self._build_data(**kwargs)
        response = await self.client.post(self.endpoint, data=data)
        return User(**response)
    
    async def update(self, user_id: int, **kwargs) -> User:
        """异步更新用户"""
        data = self._build_data(**kwargs)
        response = await self.client.post(f"{self.endpoint}/{user_id}", data=data)
        return User(**response)
    
    async def update_me(self, **kwargs) -> User:
        """异步更新当前用户信息"""
        data = self._build_data(**kwargs)
        response = await self.client.post(f"{self.endpoint}/me", data=data)
        return User(**response)
    
    async def delete(self, user_id: int, force: bool = False, reassign: Optional[int] = None) -> Dict[str, Any]:
        """异步删除用户"""
        params = {}
        if force:
            params["force"] = True
        if reassign is not None:
            params["reassign"] = reassign
        
        return await self.client.delete(f"{self.endpoint}/{user_id}")
    
    def _build_params(self, **kwargs) -> Dict[str, Any]:
        """构建查询参数"""
        params = {}
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, list):
                    params[key] = ",".join(map(str, value))
                else:
                    params[key] = value
        return params
    
    def _build_data(self, **kwargs) -> Dict[str, Any]:
        """构建请求数据"""
        data = {}
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        return data