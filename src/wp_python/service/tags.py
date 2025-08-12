"""
WordPress 标签服务

提供标签的CRUD操作，基于WordPress官方REST API文档。
标签是WordPress的非层级分类法，用于标记文章内容。
"""

from typing import List, Optional, Dict, Any

from ..core.models import Tag
from ..core.client import WordPressClient, AsyncWordPressClient


class TagService:
    """标签服务类 - 同步版本"""
    
    def __init__(self, client: WordPressClient):
        """
        初始化标签服务
        
        参数:
            client: WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "tags"
    
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
        hide_empty: Optional[bool] = None,
        post: Optional[int] = None,
        slug: Optional[List[str]] = None,
        context: str = "view",
        **kwargs
    ) -> List[Tag]:
        """
        获取标签列表
        
        参数:
            page: 页码，从1开始
            per_page: 每页标签数量，最大100
            search: 搜索关键词
            exclude: 排除的标签ID列表
            include: 包含的标签ID列表
            offset: 偏移量
            order: 排序方向 (asc/desc)
            orderby: 排序字段 (id/include/name/slug/include_slugs/term_group/description/count)
            hide_empty: 是否隐藏空标签（没有文章的标签）
            post: 关联的文章ID
            slug: 标签别名列表
            context: 响应上下文 (view/embed/edit)
            **kwargs: 其他查询参数
            
        返回:
            标签对象列表
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
        if hide_empty is not None:
            params["hide_empty"] = hide_empty
        if post is not None:
            params["post"] = post
        if slug:
            params["slug"] = ",".join(slug)
        
        # 添加额外参数
        params.update(kwargs)
        
        # 发送请求
        response = self.client.get(self.endpoint, params=params)
        
        # 转换为Tag对象列表
        return [Tag.from_api_response(tag_data) for tag_data in response]
    
    def get(self, tag_id: int, context: str = "view") -> Tag:
        """
        获取单个标签
        
        参数:
            tag_id: 标签ID
            context: 响应上下文 (view/embed/edit)
            
        返回:
            标签对象
            
        异常:
            NotFoundError: 标签不存在
        """
        params = {"context": context}
        response = self.client.get(f"{self.endpoint}/{tag_id}", params=params)
        return Tag.from_api_response(response)
    
    def create(
        self,
        name: str,
        description: Optional[str] = None,
        slug: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tag:
        """
        创建新标签
        
        参数:
            name: 标签名称
            description: 标签描述
            slug: 标签别名
            meta: 自定义字段
            **kwargs: 其他字段
            
        返回:
            创建的标签对象
            
        异常:
            ValidationError: 数据验证失败
        """
        # 构建请求数据
        data = {"name": name}
        
        # 添加可选字段
        if description is not None:
            data["description"] = description
        if slug is not None:
            data["slug"] = slug
        if meta is not None:
            data["meta"] = meta
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(self.endpoint, data=data)
        return Tag.from_api_response(response)
    
    def update(
        self,
        tag_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        slug: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tag:
        """
        更新标签
        
        参数:
            tag_id: 标签ID
            name: 标签名称
            description: 标签描述
            slug: 标签别名
            meta: 自定义字段
            **kwargs: 其他字段
            
        返回:
            更新后的标签对象
            
        异常:
            NotFoundError: 标签不存在
            ValidationError: 数据验证失败
        """
        # 构建请求数据（只包含非None的字段）
        data = {}
        
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if slug is not None:
            data["slug"] = slug
        if meta is not None:
            data["meta"] = meta
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(f"{self.endpoint}/{tag_id}", data=data)
        return Tag.from_api_response(response)
    
    def delete(self, tag_id: int, force: bool = False) -> Dict[str, Any]:
        """
        删除标签
        
        参数:
            tag_id: 标签ID
            force: 是否强制删除
            
        返回:
            删除操作的结果
            
        异常:
            NotFoundError: 标签不存在
        """
        params = {}
        if force:
            params["force"] = True
        
        return self.client.delete(f"{self.endpoint}/{tag_id}")


class AsyncTagService:
    """标签服务类 - 异步版本"""
    
    def __init__(self, client: AsyncWordPressClient):
        """
        初始化异步标签服务
        
        参数:
            client: 异步WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "tags"
    
    async def list(self, **kwargs) -> List[Tag]:
        """异步获取标签列表"""
        params = self._build_params(**kwargs)
        response = await self.client.get(self.endpoint, params=params)
        return [Tag(**tag_data) for tag_data in response]
    
    async def get(self, tag_id: int, context: str = "view") -> Tag:
        """异步获取单个标签"""
        params = {"context": context}
        response = await self.client.get(f"{self.endpoint}/{tag_id}", params=params)
        return Tag(**response)
    
    async def create(self, **kwargs) -> Tag:
        """异步创建标签"""
        data = self._build_data(**kwargs)
        response = await self.client.post(self.endpoint, data=data)
        return Tag(**response)
    
    async def update(self, tag_id: int, **kwargs) -> Tag:
        """异步更新标签"""
        data = self._build_data(**kwargs)
        response = await self.client.post(f"{self.endpoint}/{tag_id}", data=data)
        return Tag(**response)
    
    async def delete(self, tag_id: int, force: bool = False) -> Dict[str, Any]:
        """异步删除标签"""
        params = {}
        if force:
            params["force"] = True
        
        return await self.client.delete(f"{self.endpoint}/{tag_id}")
    
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