"""
WordPress 评论服务

提供评论的CRUD操作，基于WordPress官方REST API文档。
支持评论的创建、读取、更新、删除以及状态管理。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..core.models import Comment
from ..core.client import WordPressClient, AsyncWordPressClient


class CommentService:
    """评论服务类 - 同步版本"""
    
    def __init__(self, client: WordPressClient):
        """
        初始化评论服务
        
        参数:
            client: WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "comments"
    
    def list(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        after: Optional[datetime] = None,
        author: Optional[List[int]] = None,
        author_exclude: Optional[List[int]] = None,
        author_email: Optional[str] = None,
        before: Optional[datetime] = None,
        exclude: Optional[List[int]] = None,
        include: Optional[List[int]] = None,
        offset: Optional[int] = None,
        order: str = "desc",
        orderby: str = "date_gmt",
        parent: Optional[List[int]] = None,
        parent_exclude: Optional[List[int]] = None,
        post: Optional[List[int]] = None,
        status: Optional[str] = None,
        type: Optional[str] = None,
        password: Optional[str] = None,
        context: str = "view",
        **kwargs
    ) -> List[Comment]:
        """
        获取评论列表
        
        参数:
            page: 页码，从1开始
            per_page: 每页评论数量，最大100
            search: 搜索关键词
            after: 查询此日期之后的评论
            author: 作者ID列表
            author_exclude: 排除的作者ID列表
            author_email: 作者邮箱
            before: 查询此日期之前的评论
            exclude: 排除的评论ID列表
            include: 包含的评论ID列表
            offset: 偏移量
            order: 排序方向 (asc/desc)
            orderby: 排序字段 (date/date_gmt/id/include/post/parent/type)
            parent: 父评论ID列表
            parent_exclude: 排除的父评论ID列表
            post: 文章ID列表
            status: 评论状态 (hold/approve/spam/trash)
            type: 评论类型
            password: 文章密码（如果文章受密码保护）
            context: 响应上下文 (view/embed/edit)
            **kwargs: 其他查询参数
            
        返回:
            评论对象列表
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
        if after:
            params["after"] = after.isoformat()
        if author:
            params["author"] = ",".join(map(str, author))
        if author_exclude:
            params["author_exclude"] = ",".join(map(str, author_exclude))
        if author_email:
            params["author_email"] = author_email
        if before:
            params["before"] = before.isoformat()
        if exclude:
            params["exclude"] = ",".join(map(str, exclude))
        if include:
            params["include"] = ",".join(map(str, include))
        if offset is not None:
            params["offset"] = offset
        if parent:
            params["parent"] = ",".join(map(str, parent))
        if parent_exclude:
            params["parent_exclude"] = ",".join(map(str, parent_exclude))
        if post:
            params["post"] = ",".join(map(str, post))
        if status:
            params["status"] = status
        if type:
            params["type"] = type
        if password:
            params["password"] = password
        
        # 添加额外参数
        params.update(kwargs)
        
        # 发送请求
        response = self.client.get(self.endpoint, params=params)
        
        # 转换为Comment对象列表
        return [Comment.from_api_response(comment_data) for comment_data in response]
    
    def get(self, comment_id: int, context: str = "view", password: Optional[str] = None) -> Comment:
        """
        获取单个评论
        
        参数:
            comment_id: 评论ID
            context: 响应上下文 (view/embed/edit)
            password: 文章密码（如果文章受密码保护）
            
        返回:
            评论对象
            
        异常:
            NotFoundError: 评论不存在
        """
        params = {"context": context}
        if password:
            params["password"] = password
        
        response = self.client.get(f"{self.endpoint}/{comment_id}", params=params)
        return Comment.from_api_response(response)
    
    def create(
        self,
        post: int,
        content: str,
        author: Optional[int] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        author_url: Optional[str] = None,
        parent: Optional[int] = None,
        date: Optional[datetime] = None,
        date_gmt: Optional[datetime] = None,
        status: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Comment:
        """
        创建新评论
        
        参数:
            post: 文章ID
            content: 评论内容
            author: 作者ID（已登录用户）
            author_name: 作者姓名（未登录用户）
            author_email: 作者邮箱（未登录用户）
            author_url: 作者网站（未登录用户）
            parent: 父评论ID
            date: 评论日期（站点时区）
            date_gmt: 评论日期（GMT时区）
            status: 评论状态 (hold/approve)
            meta: 自定义字段
            **kwargs: 其他字段
            
        返回:
            创建的评论对象
            
        异常:
            ValidationError: 数据验证失败
        """
        # 构建请求数据
        data = {
            "post": post,
            "content": content
        }
        
        # 添加可选字段
        if author is not None:
            data["author"] = author
        if author_name is not None:
            data["author_name"] = author_name
        if author_email is not None:
            data["author_email"] = author_email
        if author_url is not None:
            data["author_url"] = author_url
        if parent is not None:
            data["parent"] = parent
        if date is not None:
            data["date"] = date.isoformat()
        if date_gmt is not None:
            data["date_gmt"] = date_gmt.isoformat()
        if status is not None:
            data["status"] = status
        if meta is not None:
            data["meta"] = meta
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(self.endpoint, data=data)
        return Comment.from_api_response(response)
    
    def update(
        self,
        comment_id: int,
        content: Optional[str] = None,
        author: Optional[int] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        author_url: Optional[str] = None,
        date: Optional[datetime] = None,
        date_gmt: Optional[datetime] = None,
        status: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Comment:
        """
        更新评论
        
        参数:
            comment_id: 评论ID
            其他参数与create方法相同（除了post不能修改）
            
        返回:
            更新后的评论对象
            
        异常:
            NotFoundError: 评论不存在
            ValidationError: 数据验证失败
        """
        # 构建请求数据（只包含非None的字段）
        data = {}
        
        if content is not None:
            data["content"] = content
        if author is not None:
            data["author"] = author
        if author_name is not None:
            data["author_name"] = author_name
        if author_email is not None:
            data["author_email"] = author_email
        if author_url is not None:
            data["author_url"] = author_url
        if date is not None:
            data["date"] = date.isoformat()
        if date_gmt is not None:
            data["date_gmt"] = date_gmt.isoformat()
        if status is not None:
            data["status"] = status
        if meta is not None:
            data["meta"] = meta
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(f"{self.endpoint}/{comment_id}", data=data)
        return Comment.from_api_response(response)
    
    def delete(self, comment_id: int, force: bool = False) -> Dict[str, Any]:
        """
        删除评论
        
        参数:
            comment_id: 评论ID
            force: 是否强制删除（跳过回收站）
            
        返回:
            删除操作的结果
            
        异常:
            NotFoundError: 评论不存在
        """
        params = {}
        if force:
            params["force"] = True
        
        return self.client.delete(f"{self.endpoint}/{comment_id}")


class AsyncCommentService:
    """评论服务类 - 异步版本"""
    
    def __init__(self, client: AsyncWordPressClient):
        """
        初始化异步评论服务
        
        参数:
            client: 异步WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "comments"
    
    async def list(self, **kwargs) -> List[Comment]:
        """异步获取评论列表"""
        params = self._build_params(**kwargs)
        response = await self.client.get(self.endpoint, params=params)
        return [Comment(**comment_data) for comment_data in response]
    
    async def get(self, comment_id: int, context: str = "view", password: Optional[str] = None) -> Comment:
        """异步获取单个评论"""
        params = {"context": context}
        if password:
            params["password"] = password
        
        response = await self.client.get(f"{self.endpoint}/{comment_id}", params=params)
        return Comment(**response)
    
    async def create(self, **kwargs) -> Comment:
        """异步创建评论"""
        data = self._build_data(**kwargs)
        response = await self.client.post(self.endpoint, data=data)
        return Comment(**response)
    
    async def update(self, comment_id: int, **kwargs) -> Comment:
        """异步更新评论"""
        data = self._build_data(**kwargs)
        response = await self.client.post(f"{self.endpoint}/{comment_id}", data=data)
        return Comment(**response)
    
    async def delete(self, comment_id: int, force: bool = False) -> Dict[str, Any]:
        """异步删除评论"""
        params = {}
        if force:
            params["force"] = True
        
        return await self.client.delete(f"{self.endpoint}/{comment_id}")
    
    def _build_params(self, **kwargs) -> Dict[str, Any]:
        """构建查询参数"""
        params = {}
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, list):
                    params[key] = ",".join(map(str, value))
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
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    data[key] = value
        return data