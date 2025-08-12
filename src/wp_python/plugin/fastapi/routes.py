"""
FastAPI WordPress 路由

提供WordPress REST API的FastAPI路由封装，自动生成RESTful API端点。
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request, Query, UploadFile, File, Form, Body

from ...utils.logger import get_logger
from ...utils.config import get_config
from ... import WordPress
from ...core.models import PostStatus


class WordPressRouter:
    """
    WordPress路由器
    
    自动生成WordPress REST API的FastAPI路由。
    """
    
    def __init__(self, wordpress_config: Optional[Dict[str, Any]] = None):
        """
        初始化路由器
        
        参数:
            wordpress_config: WordPress配置
        """
        self.config = wordpress_config or {}
        self.logger = get_logger("wordpress_router")
        self.router = APIRouter()
        self._setup_routes()
    
    def _get_wordpress_client(self, request: Request) -> WordPress:
        """
        获取WordPress客户端实例
        
        参数:
            request: FastAPI请求对象
            
        返回:
            WordPress客户端实例
        """
        # 从请求状态或配置获取WordPress配置
        wp_config = getattr(request.state, 'wordpress_config', None) or get_config()
        
        return WordPress(
            wp_config.base_url,
            **wp_config.get_auth_config(),
            **wp_config.get_client_config()
        )
    
    def _setup_routes(self) -> None:
        """设置所有路由"""
        self._setup_post_routes()
        self._setup_page_routes()
        self._setup_category_routes()
        self._setup_tag_routes()
        self._setup_user_routes()
        self._setup_media_routes()
        self._setup_comment_routes()
        self._setup_info_routes()
    
    def _setup_info_routes(self) -> None:
        """设置信息路由"""
        
        @self.router.get("/", summary="API信息", tags=["信息"])
        async def get_api_info():
            """获取API基本信息"""
            return {
                "name": "WordPress REST API",
                "version": "1.0.0",
                "description": "基于wp-python的WordPress REST API服务",
                "powered_by": "wp-python FastAPI Plugin",
                "endpoints": {
                    "posts": "/api/v1/posts",
                    "pages": "/api/v1/pages", 
                    "categories": "/api/v1/categories",
                    "tags": "/api/v1/tags",
                    "users": "/api/v1/users",
                    "media": "/api/v1/media",
                    "comments": "/api/v1/comments"
                },
                "documentation": "/docs"
            }
        
        @self.router.get("/health", summary="健康检查", tags=["信息"])
        async def health_check(request: Request):
            """健康检查端点"""
            try:
                wp = self._get_wordpress_client(request)
                connection_info = wp.test_connection()
                wp.close()
                
                return {
                    "status": "healthy",
                    "wordpress_connection": connection_info["status"],
                    "timestamp": connection_info.get("timestamp")
                }
            except Exception as e:
                self.logger.error(f"健康检查失败: {e}")
                raise HTTPException(status_code=503, detail="WordPress连接失败")
    
    def _setup_post_routes(self) -> None:
        """设置文章路由"""
        
        @self.router.get("/posts", summary="获取文章列表", tags=["文章"])
        async def get_posts(
            request: Request,
            page: int = Query(1, ge=1, description="页码"),
            per_page: int = Query(10, ge=1, le=100, description="每页数量"),
            search: Optional[str] = Query(None, description="搜索关键词"),
            status: Optional[str] = Query("publish", description="文章状态"),
            author: Optional[int] = Query(None, description="作者ID")
        ):
            """获取文章列表"""
            try:
                wp = self._get_wordpress_client(request)
                
                # 构建查询参数
                query_params = {
                    "page": page,
                    "per_page": per_page
                }
                
                if search:
                    query_params["search"] = search
                if status:
                    query_params["status"] = [status]
                if author:
                    query_params["author"] = [author]
                
                posts = wp.posts.list(**query_params)
                wp.close()
                
                # 转换为字典格式
                return {
                    "data": [post.model_dump() for post in posts],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": len(posts)
                    }
                }
                
            except Exception as e:
                self.logger.error(f"获取文章列表失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/posts/{post_id}", summary="获取单个文章", tags=["文章"])
        async def get_post(request: Request, post_id: int):
            """获取单个文章"""
            try:
                wp = self._get_wordpress_client(request)
                post = wp.posts.get(post_id)
                wp.close()
                
                return {"data": post.model_dump()}
                
            except Exception as e:
                self.logger.error(f"获取文章失败: {e}")
                if "not found" in str(e).lower():
                    raise HTTPException(status_code=404, detail="文章不存在")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/posts", summary="创建文章", tags=["文章"])
        async def create_post(
            request: Request,
            title: str,
            content: Optional[str] = None,
            status: str = "draft",
            excerpt: Optional[str] = None
        ):
            """创建新文章"""
            try:
                wp = self._get_wordpress_client(request)
                
                post = wp.posts.create(
                    title=title,
                    content=content or "",
                    status=PostStatus(status),
                    excerpt=excerpt
                )
                wp.close()
                
                return {"data": post.model_dump(), "message": "文章创建成功"}
                
            except Exception as e:
                self.logger.error(f"创建文章失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_page_routes(self) -> None:
        """设置页面路由"""
        
        @self.router.get("/pages", summary="获取页面列表", tags=["页面"])
        async def get_pages(
            request: Request,
            page: int = Query(1, ge=1),
            per_page: int = Query(10, ge=1, le=100)
        ):
            """获取页面列表"""
            try:
                wp = self._get_wordpress_client(request)
                pages = wp.pages.list(page=page, per_page=per_page)
                wp.close()
                
                return {
                    "data": [page.model_dump() for page in pages],
                    "pagination": {"page": page, "per_page": per_page}
                }
                
            except Exception as e:
                self.logger.error(f"获取页面列表失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/pages/{page_id}", summary="获取单个页面", tags=["页面"])
        async def get_page(request: Request, page_id: int):
            """获取单个页面"""
            try:
                wp = self._get_wordpress_client(request)
                page = wp.pages.get(page_id)
                wp.close()
                
                return {"data": page.model_dump()}
                
            except Exception as e:
                self.logger.error(f"获取页面失败: {e}")
                if "not found" in str(e).lower():
                    raise HTTPException(status_code=404, detail="页面不存在")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_category_routes(self) -> None:
        """设置分类路由"""
        
        @self.router.get("/categories", summary="获取分类列表", tags=["分类"])
        async def get_categories(
            request: Request,
            page: int = Query(1, ge=1),
            per_page: int = Query(10, ge=1, le=100)
        ):
            """获取分类列表"""
            try:
                wp = self._get_wordpress_client(request)
                categories = wp.categories.list(page=page, per_page=per_page)
                wp.close()
                
                return {
                    "data": [category.model_dump() for category in categories],
                    "pagination": {"page": page, "per_page": per_page}
                }
                
            except Exception as e:
                self.logger.error(f"获取分类列表失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_tag_routes(self) -> None:
        """设置标签路由"""
        
        @self.router.get("/tags", summary="获取标签列表", tags=["标签"])
        async def get_tags(
            request: Request,
            page: int = Query(1, ge=1),
            per_page: int = Query(10, ge=1, le=100)
        ):
            """获取标签列表"""
            try:
                wp = self._get_wordpress_client(request)
                tags = wp.tags.list(page=page, per_page=per_page)
                wp.close()
                
                return {
                    "data": [tag.model_dump() for tag in tags],
                    "pagination": {"page": page, "per_page": per_page}
                }
                
            except Exception as e:
                self.logger.error(f"获取标签列表失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_user_routes(self) -> None:
        """设置用户路由"""
        
        @self.router.get("/users", summary="获取用户列表", tags=["用户"])
        async def get_users(
            request: Request,
            page: int = Query(1, ge=1),
            per_page: int = Query(10, ge=1, le=100)
        ):
            """获取用户列表"""
            try:
                wp = self._get_wordpress_client(request)
                users = wp.users.list(page=page, per_page=per_page)
                wp.close()
                
                return {
                    "data": [user.model_dump() for user in users],
                    "pagination": {"page": page, "per_page": per_page}
                }
                
            except Exception as e:
                self.logger.error(f"获取用户列表失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/users/me", summary="获取当前用户", tags=["用户"])
        async def get_current_user(request: Request):
            """获取当前用户信息"""
            try:
                wp = self._get_wordpress_client(request)
                user = wp.users.get_me()
                wp.close()
                
                return {"data": user.model_dump()}
                
            except Exception as e:
                self.logger.error(f"获取当前用户失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_media_routes(self) -> None:
        """设置媒体路由"""
        
        @self.router.get("/media", summary="获取媒体列表", tags=["媒体"])
        async def get_media(
            request: Request,
            page: int = Query(1, ge=1),
            per_page: int = Query(10, ge=1, le=100),
            search: Optional[str] = Query(None),
            media_type: Optional[str] = Query(None, description="媒体类型，如 image/video/audio"),
            mime_type: Optional[str] = Query(None, description="MIME类型，如 image/jpeg")
        ):
            try:
                wp = self._get_wordpress_client(request)
                media_items = wp.media.list(
                    page=page,
                    per_page=per_page,
                    search=search,
                    media_type=media_type,
                    mime_type=mime_type
                )
                wp.close()
                return {
                    "data": [m.model_dump() for m in media_items],
                    "pagination": {"page": page, "per_page": per_page, "total": len(media_items)}
                }
            except Exception as e:
                self.logger.error(f"获取媒体列表失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/media/{media_id}", summary="获取单个媒体", tags=["媒体"])
        async def get_media_item(request: Request, media_id: int):
            try:
                wp = self._get_wordpress_client(request)
                media = wp.media.get(media_id)
                wp.close()
                return {"data": media.model_dump()}
            except Exception as e:
                self.logger.error(f"获取媒体失败: {e}")
                if "not found" in str(e).lower():
                    raise HTTPException(status_code=404, detail="媒体不存在")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/media/upload", summary="上传媒体文件", tags=["媒体"])
        async def upload_media(
            request: Request,
            file: UploadFile = File(...),
            title: Optional[str] = Form(None),
            alt_text: Optional[str] = Form(None),
            caption: Optional[str] = Form(None),
            description: Optional[str] = Form(None),
            post: Optional[int] = Form(None),
            author: Optional[int] = Form(None),
            comment_status: Optional[str] = Form(None),
            ping_status: Optional[str] = Form(None),
            template: Optional[str] = Form(None)
        ):
            try:
                wp = self._get_wordpress_client(request)
                file_bytes = await file.read()
                media = wp.media.upload_from_bytes(
                    file_data=file_bytes,
                    filename=file.filename,
                    title=title,
                    alt_text=alt_text,
                    caption=caption,
                    description=description,
                    post=post,
                    author=author,
                    comment_status=comment_status,
                    ping_status=ping_status,
                    template=template
                )
                wp.close()
                return {"data": media.model_dump(), "message": "媒体上传成功"}
            except Exception as e:
                self.logger.error(f"上传媒体失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.patch("/media/{media_id}", summary="更新媒体信息", tags=["媒体"])
        async def update_media(
            request: Request,
            media_id: int,
            title: Optional[str] = Body(None),
            alt_text: Optional[str] = Body(None),
            caption: Optional[str] = Body(None),
            description: Optional[str] = Body(None),
            post: Optional[int] = Body(None),
            author: Optional[int] = Body(None),
            comment_status: Optional[str] = Body(None),
            ping_status: Optional[str] = Body(None)
        ):
            try:
                wp = self._get_wordpress_client(request)
                media = wp.media.update(
                    media_id,
                    title=title,
                    alt_text=alt_text,
                    caption=caption,
                    description=description,
                    post=post,
                    author=author,
                    comment_status=comment_status,
                    ping_status=ping_status
                )
                wp.close()
                return {"data": media.model_dump(), "message": "媒体更新成功"}
            except Exception as e:
                self.logger.error(f"更新媒体失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.delete("/media/{media_id}", summary="删除媒体", tags=["媒体"])
        async def delete_media(request: Request, media_id: int, force: bool = Query(False)):
            try:
                wp = self._get_wordpress_client(request)
                result = wp.media.delete(media_id, force=force)
                wp.close()
                return {"data": result, "message": "媒体删除成功"}
            except Exception as e:
                self.logger.error(f"删除媒体失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_comment_routes(self) -> None:
        """设置评论路由"""
        
        @self.router.get("/comments", summary="获取评论列表", tags=["评论"])
        async def get_comments(
            request: Request,
            page: int = Query(1, ge=1),
            per_page: int = Query(10, ge=1, le=100),
            post: Optional[int] = Query(None, description="文章ID")
        ):
            try:
                wp = self._get_wordpress_client(request)
                query_params: Dict[str, Any] = {"page": page, "per_page": per_page}
                if post is not None:
                    query_params["post"] = [post]
                comments = wp.comments.list(**query_params)
                wp.close()
                return {
                    "data": [c.model_dump() for c in comments],
                    "pagination": {"page": page, "per_page": per_page, "total": len(comments)}
                }
            except Exception as e:
                self.logger.error(f"获取评论列表失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/comments/{comment_id}", summary="获取单个评论", tags=["评论"])
        async def get_comment(request: Request, comment_id: int):
            try:
                wp = self._get_wordpress_client(request)
                comment = wp.comments.get(comment_id)
                wp.close()
                return {"data": comment.model_dump()}
            except Exception as e:
                self.logger.error(f"获取评论失败: {e}")
                if "not found" in str(e).lower():
                    raise HTTPException(status_code=404, detail="评论不存在")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/comments", summary="创建评论", tags=["评论"])
        async def create_comment(
            request: Request,
            post: int,
            content: str,
            author: Optional[int] = None,
            author_name: Optional[str] = None,
            author_email: Optional[str] = None,
            author_url: Optional[str] = None,
            parent: Optional[int] = None,
            status: Optional[str] = None
        ):
            try:
                wp = self._get_wordpress_client(request)
                comment = wp.comments.create(
                    post=post,
                    content=content,
                    author=author,
                    author_name=author_name,
                    author_email=author_email,
                    author_url=author_url,
                    parent=parent,
                    status=status
                )
                wp.close()
                return {"data": comment.model_dump(), "message": "评论创建成功"}
            except Exception as e:
                self.logger.error(f"创建评论失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.patch("/comments/{comment_id}", summary="更新评论", tags=["评论"])
        async def update_comment(
            request: Request,
            comment_id: int,
            content: Optional[str] = Body(None),
            status: Optional[str] = Body(None)
        ):
            try:
                wp = self._get_wordpress_client(request)
                comment = wp.comments.update(
                    comment_id,
                    content=content,
                    status=status
                )
                wp.close()
                return {"data": comment.model_dump(), "message": "评论更新成功"}
            except Exception as e:
                self.logger.error(f"更新评论失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.delete("/comments/{comment_id}", summary="删除评论", tags=["评论"])
        async def delete_comment(request: Request, comment_id: int, force: bool = Query(False)):
            try:
                wp = self._get_wordpress_client(request)
                result = wp.comments.delete(comment_id, force=force)
                wp.close()
                return {"data": result, "message": "评论删除成功"}
            except Exception as e:
                self.logger.error(f"删除评论失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def get_router(self) -> APIRouter:
        """
        获取路由器实例
        
        返回:
            FastAPI路由器
        """
        return self.router