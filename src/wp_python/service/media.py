"""
WordPress 媒体服务

提供媒体文件的CRUD操作，基于WordPress官方REST API文档。
支持图片、视频、音频等各种媒体文件的上传和管理。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import os

from ..core.models import Media
from ..core.client import WordPressClient, AsyncWordPressClient


class MediaService:
    """媒体服务类 - 同步版本"""
    
    def __init__(self, client: WordPressClient):
        """
        初始化媒体服务
        
        参数:
            client: WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "media"
    
    def list(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        after: Optional[datetime] = None,
        author: Optional[List[int]] = None,
        author_exclude: Optional[List[int]] = None,
        before: Optional[datetime] = None,
        exclude: Optional[List[int]] = None,
        include: Optional[List[int]] = None,
        offset: Optional[int] = None,
        order: str = "desc",
        orderby: str = "date",
        parent: Optional[List[int]] = None,
        parent_exclude: Optional[List[int]] = None,
        slug: Optional[List[str]] = None,
        status: Optional[str] = None,
        media_type: Optional[str] = None,
        mime_type: Optional[str] = None,
        context: str = "view",
        **kwargs
    ) -> List[Media]:
        """
        获取媒体列表
        
        参数:
            page: 页码，从1开始
            per_page: 每页媒体数量，最大100
            search: 搜索关键词
            after: 查询此日期之后上传的媒体
            author: 作者ID列表
            author_exclude: 排除的作者ID列表
            before: 查询此日期之前上传的媒体
            exclude: 排除的媒体ID列表
            include: 包含的媒体ID列表
            offset: 偏移量
            order: 排序方向 (asc/desc)
            orderby: 排序字段 (author/date/id/include/modified/parent/relevance/slug/title)
            parent: 父文章ID列表
            parent_exclude: 排除的父文章ID列表
            slug: 媒体别名列表
            status: 媒体状态
            media_type: 媒体类型 (image/video/text/application/audio)
            mime_type: MIME类型
            context: 响应上下文 (view/embed/edit)
            **kwargs: 其他查询参数
            
        返回:
            媒体对象列表
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
        if slug:
            params["slug"] = ",".join(slug)
        if status:
            params["status"] = status
        if media_type:
            params["media_type"] = media_type
        if mime_type:
            params["mime_type"] = mime_type
        
        # 添加额外参数
        params.update(kwargs)
        
        # 发送请求
        response = self.client.get(self.endpoint, params=params)
        
        # 转换为Media对象列表
        return [Media.from_api_response(media_data) for media_data in response]
    
    def get(self, media_id: int, context: str = "view") -> Media:
        """
        获取单个媒体
        
        参数:
            media_id: 媒体ID
            context: 响应上下文 (view/embed/edit)
            
        返回:
            媒体对象
            
        异常:
            NotFoundError: 媒体不存在
        """
        params = {"context": context}
        response = self.client.get(f"{self.endpoint}/{media_id}", params=params)
        return Media.from_api_response(response)
    
    def upload(
        self,
        file_path: str,
        title: Optional[str] = None,
        alt_text: Optional[str] = None,
        caption: Optional[str] = None,
        description: Optional[str] = None,
        post: Optional[int] = None,
        author: Optional[int] = None,
        comment_status: Optional[str] = None,
        ping_status: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        template: Optional[str] = None,
        **kwargs
    ) -> Media:
        """
        上传媒体文件
        
        参数:
            file_path: 文件路径
            title: 媒体标题
            alt_text: 替代文本（用于图片）
            caption: 媒体说明
            description: 媒体描述
            post: 关联的文章ID
            author: 作者ID
            comment_status: 评论状态 (open/closed)
            ping_status: Ping状态 (open/closed)
            meta: 自定义字段
            template: 模板
            **kwargs: 其他字段
            
        返回:
            上传的媒体对象
            
        异常:
            ValidationError: 文件验证失败
            FileNotFoundError: 文件不存在
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 准备文件上传
        filename = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, self._get_mime_type(file_path))}
            
            # 构建请求数据
            data = {}
            
            if title is not None:
                data["title"] = title
            if alt_text is not None:
                data["alt_text"] = alt_text
            if caption is not None:
                data["caption"] = caption
            if description is not None:
                data["description"] = description
            if post is not None:
                data["post"] = post
            if author is not None:
                data["author"] = author
            if comment_status is not None:
                data["comment_status"] = comment_status
            if ping_status is not None:
                data["ping_status"] = ping_status
            if meta is not None:
                data["meta"] = meta
            if template is not None:
                data["template"] = template
            
            # 添加额外字段
            data.update(kwargs)
            
            # 发送请求
            response = self.client.post(self.endpoint, data=data, files=files)
            return Media.from_api_response(response)
    
    def upload_from_bytes(
        self,
        file_data: bytes,
        filename: str,
        mime_type: Optional[str] = None,
        **kwargs
    ) -> Media:
        """
        从字节数据上传媒体文件
        
        参数:
            file_data: 文件字节数据
            filename: 文件名
            mime_type: MIME类型
            **kwargs: 其他参数（与upload方法相同）
            
        返回:
            上传的媒体对象
        """
        # 如果没有提供MIME类型，尝试从文件扩展名推断
        if mime_type is None:
            mime_type = self._get_mime_type(filename)
        
        # 准备文件上传
        files = {'file': (filename, file_data, mime_type)}
        
        # 构建请求数据
        data = {}
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        
        # 发送请求
        response = self.client.post(self.endpoint, data=data, files=files)
        return Media.from_api_response(response)
    
    def update(
        self,
        media_id: int,
        title: Optional[str] = None,
        alt_text: Optional[str] = None,
        caption: Optional[str] = None,
        description: Optional[str] = None,
        post: Optional[int] = None,
        author: Optional[int] = None,
        comment_status: Optional[str] = None,
        ping_status: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Media:
        """
        更新媒体信息
        
        参数:
            media_id: 媒体ID
            其他参数与upload方法相同
            
        返回:
            更新后的媒体对象
            
        异常:
            NotFoundError: 媒体不存在
            ValidationError: 数据验证失败
        """
        # 构建请求数据（只包含非None的字段）
        data = {}
        
        if title is not None:
            data["title"] = title
        if alt_text is not None:
            data["alt_text"] = alt_text
        if caption is not None:
            data["caption"] = caption
        if description is not None:
            data["description"] = description
        if post is not None:
            data["post"] = post
        if author is not None:
            data["author"] = author
        if comment_status is not None:
            data["comment_status"] = comment_status
        if ping_status is not None:
            data["ping_status"] = ping_status
        if meta is not None:
            data["meta"] = meta
        
        # 添加额外字段
        data.update(kwargs)
        
        # 发送请求
        response = self.client.post(f"{self.endpoint}/{media_id}", data=data)
        return Media.from_api_response(response)
    
    def delete(self, media_id: int, force: bool = False) -> Dict[str, Any]:
        """
        删除媒体
        
        参数:
            media_id: 媒体ID
            force: 是否强制删除
            
        返回:
            删除操作的结果
            
        异常:
            NotFoundError: 媒体不存在
        """
        params = {}
        if force:
            params["force"] = True
        
        return self.client.delete(f"{self.endpoint}/{media_id}")
    
    def _get_mime_type(self, filename: str) -> str:
        """
        根据文件扩展名获取MIME类型
        
        参数:
            filename: 文件名
            
        返回:
            MIME类型
        """
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'


class AsyncMediaService:
    """媒体服务类 - 异步版本"""
    
    def __init__(self, client: AsyncWordPressClient):
        """
        初始化异步媒体服务
        
        参数:
            client: 异步WordPress HTTP客户端
        """
        self.client = client
        self.endpoint = "media"
    
    async def list(self, **kwargs) -> List[Media]:
        """异步获取媒体列表"""
        params = self._build_params(**kwargs)
        response = await self.client.get(self.endpoint, params=params)
        return [Media(**media_data) for media_data in response]
    
    async def get(self, media_id: int, context: str = "view") -> Media:
        """异步获取单个媒体"""
        params = {"context": context}
        response = await self.client.get(f"{self.endpoint}/{media_id}", params=params)
        return Media(**response)
    
    async def upload(self, file_path: str, **kwargs) -> Media:
        """异步上传媒体文件"""
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 准备文件上传
        filename = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            file_data = f.read()
            files = {'file': (filename, file_data, self._get_mime_type(file_path))}
            
            # 构建请求数据
            data = self._build_data(**kwargs)
            
            # 发送请求
            response = await self.client.post(self.endpoint, data=data, files=files)
            return Media(**response)
    
    async def upload_from_bytes(self, file_data: bytes, filename: str, 
                               mime_type: Optional[str] = None, **kwargs) -> Media:
        """异步从字节数据上传媒体文件"""
        if mime_type is None:
            mime_type = self._get_mime_type(filename)
        
        files = {'file': (filename, file_data, mime_type)}
        data = self._build_data(**kwargs)
        
        response = await self.client.post(self.endpoint, data=data, files=files)
        return Media(**response)
    
    async def update(self, media_id: int, **kwargs) -> Media:
        """异步更新媒体"""
        data = self._build_data(**kwargs)
        response = await self.client.post(f"{self.endpoint}/{media_id}", data=data)
        return Media(**response)
    
    async def delete(self, media_id: int, force: bool = False) -> Dict[str, Any]:
        """异步删除媒体"""
        params = {}
        if force:
            params["force"] = True
        
        return await self.client.delete(f"{self.endpoint}/{media_id}")
    
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
                data[key] = value
        return data
    
    def _get_mime_type(self, filename: str) -> str:
        """根据文件扩展名获取MIME类型"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'