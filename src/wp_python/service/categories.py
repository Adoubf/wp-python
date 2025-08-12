"""
WordPress 分类服务

提供分类的CRUD操作，基于WordPress官方REST API文档。
分类是WordPress的层级分类法，用于组织文章内容。
"""

from typing import List, Optional, Dict, Any

from ..core.models import Category
from ..core.client import WordPressClient, AsyncWordPressClient


class CategoryService:
    """分类服务类 - 同步版本"""
    
    def __init__(self, client: WordPressClient):
        """
        初始化分类服务
        
        参数:
            client: WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "categories"
    
    def list(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        exclude: Optional[List[int]] = None,
        include: Optional[List[int]] = None,
        order: str = "asc",
        orderby: str = "name",
        hide_empty: Optional[bool] = None,
        parent: Optional[int] = None,
        post: Optional[int] = None,
        slug: Optional[List[str]] = None,
        context: str = "view",
        **kwargs
    ) -> List[Category]:
        """
        获取分类列表
        
        参数:
            page: 页码，从1开始
            per_page: 每页分类数量，最大100
            search: 搜索关键词
            exclude: 排除的分类ID列表
            include: 包含的分类ID列表
            order: 排序方向 (asc/desc)
            orderby: 排序字段 (id/include/name/slug/include_slugs/term_group/description/count)
            hide_empty: 是否隐藏空分类（没有文章的分类）
            parent: 父分类ID
            post: 关联的文章ID
            slug: 分类别名列表
            context: 响应上下文 (view/embed/edit)
            **kwargs: 其他查询参数
            
        返回:
            分类对象列表
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
        if hide_empty is not None:
            params["hide_empty"] = hide_empty
        if parent is not None:
            params["parent"] = parent
        if post is not None:
            params["post"] = post
        if slug:
            params["slug"] = ",".join(slug)
        
        # 添加额外参数
        params.update(kwargs)
        
        # 发送请求
        response = self.client.get(self.endpoint, params=params)
        
        # 转换为Category对象列表
        return [Category.from_api_response(category_data) for category_data in response]
    
    def get(self, category_id: int, context: str = "view") -> Category:
        """
        获取单个分类
        
        参数:
            category_id: 分类ID
            context: 响应上下文 (view/embed/edit)
            
        返回:
            分类对象
            
        异常:
            NotFoundError: 分类不存在
        """
        params = {"context": context}
        response = self.client.get(f"{self.endpoint}/{category_id}", params=params)
        return Category.from_api_response(response)
    
    def create(
        self,
        name: str,
        description: Optional[str] = None,
        slug: Optional[str] = None,
        parent: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Category:
        """
        创建新分类
        
        参数:
            name: 分类名称
            description: 分类描述
            slug: 分类别名
            parent: 父分类ID
            meta: 自定义字段
            **kwargs: 其他字段
            
        返回:
            创建的分类对象
            
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
        if parent is not None:
            data["parent"] = parent
        if meta is not None:
            data["meta"] = meta
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(self.endpoint, data=data)
        return Category.from_api_response(response)
    
    def update(
        self,
        category_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        slug: Optional[str] = None,
        parent: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Category:
        """
        更新分类
        
        参数:
            category_id: 分类ID
            name: 分类名称
            description: 分类描述
            slug: 分类别名
            parent: 父分类ID
            meta: 自定义字段
            **kwargs: 其他字段
            
        返回:
            更新后的分类对象
            
        异常:
            NotFoundError: 分类不存在
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
        if parent is not None:
            data["parent"] = parent
        if meta is not None:
            data["meta"] = meta
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(f"{self.endpoint}/{category_id}", data=data)
        return Category.from_api_response(response)
    
    def delete(self, category_id: int, force: bool = False) -> Dict[str, Any]:
        """
        删除分类
        
        参数:
            category_id: 分类ID
            force: 是否强制删除
            
        返回:
            删除操作的结果
            
        异常:
            NotFoundError: 分类不存在
        """
        params = {}
        if force:
            params["force"] = True
        
        return self.client.delete(f"{self.endpoint}/{category_id}")


class AsyncCategoryService:
    """分类服务类 - 异步版本"""
    
    def __init__(self, client: AsyncWordPressClient):
        """
        初始化异步分类服务
        
        参数:
            client: 异步WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "categories"
    
    async def list(self, **kwargs) -> List[Category]:
        """异步获取分类列表"""
        params = self._build_params(**kwargs)
        response = await self.client.get(self.endpoint, params=params)
        return [Category.from_api_response(category_data) for category_data in response]
    
    async def get(self, category_id: int, context: str = "view") -> Category:
        """异步获取单个分类"""
        params = {"context": context}
        response = await self.client.get(f"{self.endpoint}/{category_id}", params=params)
        return Category(**response)
    
    async def create(self, **kwargs) -> Category:
        """异步创建分类"""
        data = self._build_data(**kwargs)
        response = await self.client.post(self.endpoint, data=data)
        return Category(**response)
    
    async def update(self, category_id: int, **kwargs) -> Category:
        """异步更新分类"""
        data = self._build_data(**kwargs)
        response = await self.client.post(f"{self.endpoint}/{category_id}", data=data)
        return Category(**response)
    
    async def delete(self, category_id: int, force: bool = False) -> Dict[str, Any]:
        """异步删除分类"""
        params = {}
        if force:
            params["force"] = True
        
        return await self.client.delete(f"{self.endpoint}/{category_id}")
    
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