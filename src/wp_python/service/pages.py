"""
WordPress 页面服务

提供页面的CRUD操作，基于WordPress官方REST API文档。
页面与文章类似，但具有层级结构和不同的默认设置。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..core.models import Page, PostStatus
from ..core.client import WordPressClient, AsyncWordPressClient
from ..utils.helpers import build_comma_separated_param


class PageService:
    """页面服务类 - 同步版本"""
    
    def __init__(self, client: WordPressClient):
        """
        初始化页面服务
        
        参数:
            client: WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "pages"
    
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
        menu_order: Optional[int] = None,
        offset: Optional[int] = None,
        order: str = "desc",
        orderby: str = "date",
        parent: Optional[List[int]] = None,
        parent_exclude: Optional[List[int]] = None,
        slug: Optional[List[str]] = None,
        status: Optional[List[PostStatus]] = None,
        context: str = "view",
        **kwargs
    ) -> List[Page]:
        """
        获取页面列表
        
        参数:
            page: 页码，从1开始
            per_page: 每页页面数量，最大100
            search: 搜索关键词
            author: 作者ID列表
            author_exclude: 排除的作者ID列表
            after: 查询此日期之后发布的页面
            before: 查询此日期之前发布的页面
            exclude: 排除的页面ID列表
            include: 包含的页面ID列表
            menu_order: 菜单排序
            offset: 偏移量
            order: 排序方向 (asc/desc)
            orderby: 排序字段 (author/date/id/include/modified/parent/relevance/slug/title/menu_order)
            parent: 父页面ID列表
            parent_exclude: 排除的父页面ID列表
            slug: 页面别名列表
            status: 页面状态列表
            context: 响应上下文 (view/embed/edit)
            **kwargs: 其他查询参数
            
        返回:
            页面对象列表
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
        if menu_order is not None:
            params["menu_order"] = menu_order
        if offset is not None:
            params["offset"] = offset
        if parent:
            params["parent"] = ",".join(map(str, parent))
        if parent_exclude:
            params["parent_exclude"] = ",".join(map(str, parent_exclude))
        if slug:
            params["slug"] = ",".join(slug)
        if status:
            params["status"] = build_comma_separated_param(status)
        
        # 添加额外参数
        params.update(kwargs)
        
        # 发送请求
        response = self.client.get(self.endpoint, params=params)
        
        # 转换为Page对象列表
        return [Page.from_api_response(page_data) for page_data in response]
    
    def get(self, page_id: int, context: str = "view", password: Optional[str] = None) -> Page:
        """
        获取单个页面
        
        参数:
            page_id: 页面ID
            context: 响应上下文 (view/embed/edit)
            password: 页面密码（如果页面受密码保护）
            
        返回:
            页面对象
            
        异常:
            NotFoundError: 页面不存在
        """
        params = {"context": context}
        if password:
            params["password"] = password
        
        response = self.client.get(f"{self.endpoint}/{page_id}", params=params)
        return Page.from_api_response(response)
    
    def create(
        self,
        title: str,
        content: Optional[str] = None,
        excerpt: Optional[str] = None,
        status: PostStatus = PostStatus.DRAFT,
        author: Optional[int] = None,
        featured_media: Optional[int] = None,
        parent: Optional[int] = None,
        menu_order: Optional[int] = None,
        comment_status: Optional[str] = None,
        ping_status: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        template: Optional[str] = None,
        date: Optional[datetime] = None,
        date_gmt: Optional[datetime] = None,
        password: Optional[str] = None,
        slug: Optional[str] = None,
        **kwargs
    ) -> Page:
        """
        创建新页面
        
        参数:
            title: 页面标题
            content: 页面内容
            excerpt: 页面摘要
            status: 页面状态
            author: 作者ID
            featured_media: 特色图片ID
            parent: 父页面ID
            menu_order: 菜单排序
            comment_status: 评论状态 (open/closed)
            ping_status: Ping状态 (open/closed)
            meta: 自定义字段
            template: 页面模板
            date: 发布日期（站点时区）
            date_gmt: 发布日期（GMT时区）
            password: 页面密码
            slug: 页面别名
            **kwargs: 其他字段
            
        返回:
            创建的页面对象
            
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
        if parent is not None:
            data["parent"] = parent
        if menu_order is not None:
            data["menu_order"] = menu_order
        if comment_status is not None:
            data["comment_status"] = comment_status
        if ping_status is not None:
            data["ping_status"] = ping_status
        if meta is not None:
            data["meta"] = meta
        if template is not None:
            data["template"] = template
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
        return Page(**response)
    
    def update(self, page_id: int, **kwargs) -> Page:
        """
        更新页面
        
        参数:
            page_id: 页面ID
            **kwargs: 更新字段（与create方法相同）
            
        返回:
            更新后的页面对象
            
        异常:
            NotFoundError: 页面不存在
            ValidationError: 数据验证失败
        """
        # 构建请求数据（只包含非None的字段）
        data = {}
        
        for key, value in kwargs.items():
            if value is not None:
                if hasattr(value, 'value'):  # 枚举类型
                    data[key] = value.value
                elif isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    data[key] = value
        
        # 发送请求
        response = self.client.post(f"{self.endpoint}/{page_id}", data=data)
        return Page(**response)
    
    def delete(self, page_id: int, force: bool = False) -> Dict[str, Any]:
        """
        删除页面
        
        参数:
            page_id: 页面ID
            force: 是否强制删除（跳过回收站）
            
        返回:
            删除操作的结果
            
        异常:
            NotFoundError: 页面不存在
        """
        params = {}
        if force:
            params["force"] = True
        
        return self.client.delete(f"{self.endpoint}/{page_id}")
    
    def get_revisions(self, page_id: int, context: str = "view") -> List[Dict[str, Any]]:
        """
        获取页面修订版本
        
        参数:
            page_id: 页面ID
            context: 响应上下文
            
        返回:
            修订版本列表
        """
        params = {"context": context}
        return self.client.get(f"{self.endpoint}/{page_id}/revisions", params=params)


class AsyncPageService:
    """页面服务类 - 异步版本"""
    
    def __init__(self, client: AsyncWordPressClient):
        """
        初始化异步页面服务
        
        参数:
            client: 异步WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "pages"
    
    async def list(self, **kwargs) -> List[Page]:
        """异步获取页面列表"""
        params = self._build_params(**kwargs)
        response = await self.client.get(self.endpoint, params=params)
        return [Page.from_api_response(page_data) for page_data in response]
    
    async def get(self, page_id: int, context: str = "view", password: Optional[str] = None) -> Page:
        """异步获取单个页面"""
        params = {"context": context}
        if password:
            params["password"] = password
        
        response = await self.client.get(f"{self.endpoint}/{page_id}", params=params)
        return Page(**response)
    
    async def create(self, **kwargs) -> Page:
        """异步创建页面"""
        data = self._build_data(**kwargs)
        response = await self.client.post(self.endpoint, data=data)
        return Page(**response)
    
    async def update(self, page_id: int, **kwargs) -> Page:
        """异步更新页面"""
        data = self._build_data(**kwargs)
        response = await self.client.post(f"{self.endpoint}/{page_id}", data=data)
        return Page(**response)
    
    async def delete(self, page_id: int, force: bool = False) -> Dict[str, Any]:
        """异步删除页面"""
        params = {}
        if force:
            params["force"] = True
        
        return await self.client.delete(f"{self.endpoint}/{page_id}")
    
    def _build_params(self, **kwargs) -> Dict[str, Any]:
        """构建查询参数"""
        params = {}
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, list):
                    if value and hasattr(value[0], 'value'):  # 枚举类型
                        params[key] = ",".join([v.value for v in value])
                    else:
                        params[key] = ",".join(map(str, value))
                elif hasattr(value, 'value'):  # 单个枚举类型
                    params[key] = value.value
                elif isinstance(value, datetime):
                    params[key] = value.isoformat()
                else:
                    params[key] = value
        return params
    
    def _build_data(self, **kwargs) -> Dict[str, Any]:
        """构建请求数据"""
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