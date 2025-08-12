"""
WordPress 文章服务

提供文章的CRUD操作，基于WordPress官方REST API文档。
支持文章的创建、读取、更新、删除以及高级查询功能。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..core.models import Post, PostStatus, PostFormat
from ..core.client import WordPressClient, AsyncWordPressClient
from ..utils.helpers import build_comma_separated_param


class PostService:
    """文章服务类 - 同步版本"""
    
    def __init__(self, client: WordPressClient):
        """
        初始化文章服务
        
        参数:
            client: WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "posts"
    
    def list(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        author: Optional[List[int]] = None,
        author_exclude: Optional[List[int]] = None,
        after: Optional[datetime] = None,
        before: Optional[datetime] = None,
        exclude: Optional[List[int]] = None,
        include: Optional[List[int]] = None,
        offset: Optional[int] = None,
        order: str = "desc",
        orderby: str = "date",
        slug: Optional[List[str]] = None,
        status: Optional[List[PostStatus]] = None,
        categories: Optional[List[int]] = None,
        categories_exclude: Optional[List[int]] = None,
        tags: Optional[List[int]] = None,
        tags_exclude: Optional[List[int]] = None,
        sticky: Optional[bool] = None,
        format: Optional[List[PostFormat]] = None,
        context: str = "view",
        **kwargs
    ) -> List[Post]:
        """
        获取文章列表
        
        参数:
            page: 页码，从1开始
            per_page: 每页文章数量，最大100
            search: 搜索关键词
            author: 作者ID列表
            author_exclude: 排除的作者ID列表
            after: 查询此日期之后发布的文章
            before: 查询此日期之前发布的文章
            exclude: 排除的文章ID列表
            include: 包含的文章ID列表
            offset: 偏移量
            order: 排序方向 (asc/desc)
            orderby: 排序字段 (author/date/id/include/modified/parent/relevance/slug/title)
            slug: 文章别名列表
            status: 文章状态列表
            categories: 分类ID列表
            categories_exclude: 排除的分类ID列表
            tags: 标签ID列表
            tags_exclude: 排除的标签ID列表
            sticky: 是否只查询置顶文章
            format: 文章格式列表
            context: 响应上下文 (view/embed/edit)
            **kwargs: 其他查询参数
            
        返回:
            文章对象列表
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
        if author:
            params["author"] = ",".join(map(str, author))
        if author_exclude:
            params["author_exclude"] = ",".join(map(str, author_exclude))
        if after:
            params["after"] = after.isoformat()
        if before:
            params["before"] = before.isoformat()
        if exclude:
            params["exclude"] = ",".join(map(str, exclude))
        if include:
            params["include"] = ",".join(map(str, include))
        if offset is not None:
            params["offset"] = offset
        if slug:
            params["slug"] = ",".join(slug)
        if status:
            params["status"] = build_comma_separated_param(status)
        if categories:
            params["categories"] = ",".join(map(str, categories))
        if categories_exclude:
            params["categories_exclude"] = ",".join(map(str, categories_exclude))
        if tags:
            params["tags"] = ",".join(map(str, tags))
        if tags_exclude:
            params["tags_exclude"] = ",".join(map(str, tags_exclude))
        if sticky is not None:
            params["sticky"] = sticky
        if format:
            params["format"] = build_comma_separated_param(format)
        
        # 添加额外参数
        params.update(kwargs)
        
        # 发送请求
        response = self.client.get(self.endpoint, params=params)
        
        # 转换为Post对象列表
        return [Post(**post_data) for post_data in response]
    
    def get(self, post_id: int, context: str = "view", password: Optional[str] = None) -> Post:
        """
        获取单个文章
        
        参数:
            post_id: 文章ID
            context: 响应上下文 (view/embed/edit)
            password: 文章密码（如果文章受密码保护）
            
        返回:
            文章对象
            
        异常:
            NotFoundError: 文章不存在
        """
        params = {"context": context}
        if password:
            params["password"] = password
        
        response = self.client.get(f"{self.endpoint}/{post_id}", params=params)
        return Post.from_api_response(response)
    
    def create(
        self,
        title: str,
        content: Optional[str] = None,
        excerpt: Optional[str] = None,
        status: PostStatus = PostStatus.DRAFT,
        author: Optional[int] = None,
        featured_media: Optional[int] = None,
        comment_status: Optional[str] = None,
        ping_status: Optional[str] = None,
        format: Optional[PostFormat] = None,
        meta: Optional[Dict[str, Any]] = None,
        sticky: Optional[bool] = None,
        template: Optional[str] = None,
        categories: Optional[List[int]] = None,
        tags: Optional[List[int]] = None,
        date: Optional[datetime] = None,
        date_gmt: Optional[datetime] = None,
        password: Optional[str] = None,
        slug: Optional[str] = None,
        **kwargs
    ) -> Post:
        """
        创建新文章
        
        参数:
            title: 文章标题
            content: 文章内容
            excerpt: 文章摘要
            status: 文章状态
            author: 作者ID
            featured_media: 特色图片ID
            comment_status: 评论状态 (open/closed)
            ping_status: Ping状态 (open/closed)
            format: 文章格式
            meta: 自定义字段
            sticky: 是否置顶
            template: 页面模板
            categories: 分类ID列表
            tags: 标签ID列表
            date: 发布日期（站点时区）
            date_gmt: 发布日期（GMT时区）
            password: 文章密码
            slug: 文章别名
            **kwargs: 其他字段
            
        返回:
            创建的文章对象
            
        异常:
            ValidationError: 数据验证失败
        """
        # 构建请求数据
        data = {
            "title": title,
            "status": status.value
        }
        
        # 添加可选字段
        if content is not None:
            data["content"] = content
        if excerpt is not None:
            data["excerpt"] = excerpt
        if author is not None:
            data["author"] = author
        if featured_media is not None:
            data["featured_media"] = featured_media
        if comment_status is not None:
            data["comment_status"] = comment_status
        if ping_status is not None:
            data["ping_status"] = ping_status
        if format is not None:
            data["format"] = format.value
        if meta is not None:
            data["meta"] = meta
        if sticky is not None:
            data["sticky"] = sticky
        if template is not None:
            data["template"] = template
        if categories is not None:
            data["categories"] = categories
        if tags is not None:
            data["tags"] = tags
        if date is not None:
            data["date"] = date.isoformat()
        if date_gmt is not None:
            data["date_gmt"] = date_gmt.isoformat()
        if password is not None:
            data["password"] = password
        if slug is not None:
            data["slug"] = slug
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(self.endpoint, data=data)
        return Post.from_api_response(response)
    
    def update(
        self,
        post_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        excerpt: Optional[str] = None,
        status: Optional[PostStatus] = None,
        author: Optional[int] = None,
        featured_media: Optional[int] = None,
        comment_status: Optional[str] = None,
        ping_status: Optional[str] = None,
        format: Optional[PostFormat] = None,
        meta: Optional[Dict[str, Any]] = None,
        sticky: Optional[bool] = None,
        template: Optional[str] = None,
        categories: Optional[List[int]] = None,
        tags: Optional[List[int]] = None,
        date: Optional[datetime] = None,
        date_gmt: Optional[datetime] = None,
        password: Optional[str] = None,
        slug: Optional[str] = None,
        **kwargs
    ) -> Post:
        """
        更新文章
        
        参数:
            post_id: 文章ID
            其他参数与create方法相同
            
        返回:
            更新后的文章对象
            
        异常:
            NotFoundError: 文章不存在
            ValidationError: 数据验证失败
        """
        # 构建请求数据（只包含非None的字段）
        data = {}
        
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        if excerpt is not None:
            data["excerpt"] = excerpt
        if status is not None:
            data["status"] = status.value
        if author is not None:
            data["author"] = author
        if featured_media is not None:
            data["featured_media"] = featured_media
        if comment_status is not None:
            data["comment_status"] = comment_status
        if ping_status is not None:
            data["ping_status"] = ping_status
        if format is not None:
            data["format"] = format.value
        if meta is not None:
            data["meta"] = meta
        if sticky is not None:
            data["sticky"] = sticky
        if template is not None:
            data["template"] = template
        if categories is not None:
            data["categories"] = categories
        if tags is not None:
            data["tags"] = tags
        if date is not None:
            data["date"] = date.isoformat()
        if date_gmt is not None:
            data["date_gmt"] = date_gmt.isoformat()
        if password is not None:
            data["password"] = password
        if slug is not None:
            data["slug"] = slug
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(f"{self.endpoint}/{post_id}", data=data)
        return Post.from_api_response(response)
    
    def delete(self, post_id: int, force: bool = False) -> Dict[str, Any]:
        """
        删除文章
        
        参数:
            post_id: 文章ID
            force: 是否强制删除（跳过回收站）
            
        返回:
            删除操作的结果
            
        异常:
            NotFoundError: 文章不存在
        """
        params = {}
        if force:
            params["force"] = True
        
        return self.client.delete(f"{self.endpoint}/{post_id}")
    
    def get_revisions(self, post_id: int, context: str = "view") -> List[Dict[str, Any]]:
        """
        获取文章修订版本
        
        参数:
            post_id: 文章ID
            context: 响应上下文
            
        返回:
            修订版本列表
        """
        params = {"context": context}
        return self.client.get(f"{self.endpoint}/{post_id}/revisions", params=params)
    
    def get_revision(self, post_id: int, revision_id: int, context: str = "view") -> Dict[str, Any]:
        """
        获取特定修订版本
        
        参数:
            post_id: 文章ID
            revision_id: 修订版本ID
            context: 响应上下文
            
        返回:
            修订版本数据
        """
        params = {"context": context}
        return self.client.get(f"{self.endpoint}/{post_id}/revisions/{revision_id}", params=params)


class AsyncPostService:
    """文章服务类 - 异步版本"""
    
    def __init__(self, client: AsyncWordPressClient):
        """
        初始化异步文章服务
        
        参数:
            client: 异步WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "posts"
    
    async def list(self, **kwargs) -> List[Post]:
        """异步获取文章列表，参数与同步版本相同"""
        # 构建查询参数（与同步版本相同的逻辑）
        params = self._build_list_params(**kwargs)
        
        # 发送异步请求
        response = await self.client.get(self.endpoint, params=params)
        
        # 转换为Post对象列表
        return [Post.from_api_response(post_data) for post_data in response]
    
    async def get(self, post_id: int, context: str = "view", password: Optional[str] = None) -> Post:
        """异步获取单个文章"""
        params = {"context": context}
        if password:
            params["password"] = password
        
        response = await self.client.get(f"{self.endpoint}/{post_id}", params=params)
        return Post.from_api_response(response)
    
    async def create(self, **kwargs) -> Post:
        """异步创建文章"""
        data = self._build_create_data(**kwargs)
        response = await self.client.post(self.endpoint, data=data)
        return Post.from_api_response(response)
    
    async def update(self, post_id: int, **kwargs) -> Post:
        """异步更新文章"""
        data = self._build_update_data(**kwargs)
        response = await self.client.post(f"{self.endpoint}/{post_id}", data=data)
        return Post.from_api_response(response)
    
    async def delete(self, post_id: int, force: bool = False) -> Dict[str, Any]:
        """异步删除文章"""
        params = {}
        if force:
            params["force"] = True
        
        return await self.client.delete(f"{self.endpoint}/{post_id}")
    
    def _build_list_params(self, **kwargs) -> Dict[str, Any]:
        """构建列表查询参数（支持枚举和字符串混合）"""
        params = {}
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, list):
                    if value:  # 非空列表
                        # 检查是否包含枚举或字符串，统一处理
                        params[key] = build_comma_separated_param(value)
                elif hasattr(value, 'value'):  # 单个枚举类型
                    params[key] = value.value
                elif isinstance(value, datetime):
                    params[key] = value.isoformat()
                else:
                    params[key] = value
        return params
    
    def _build_create_data(self, **kwargs) -> Dict[str, Any]:
        """构建创建请求数据"""
        data = {}
        for key, value in kwargs.items():
            if value is not None:
                if hasattr(value, 'value'):  # 枚举类型
                    data[key] = value.value
                elif isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    data[key] = value
        return data
    
    def _build_update_data(self, **kwargs) -> Dict[str, Any]:
        """构建更新请求数据"""
        return self._build_create_data(**kwargs)