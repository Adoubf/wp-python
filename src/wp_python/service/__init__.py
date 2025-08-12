"""
WordPress REST API 服务模块

包含所有WordPress REST API端点的服务类，
提供对文章、页面、用户、媒体等资源的操作。
"""

from .posts import PostService, AsyncPostService
from .pages import PageService, AsyncPageService
from .categories import CategoryService, AsyncCategoryService
from .tags import TagService, AsyncTagService
from .users import UserService, AsyncUserService
from .media import MediaService, AsyncMediaService
from .comments import CommentService, AsyncCommentService

# 导出所有服务类
__all__ = [
    # 同步服务
    "PostService",
    "PageService", 
    "CategoryService",
    "TagService",
    "UserService",
    "MediaService",
    "CommentService",
    
    # 异步服务
    "AsyncPostService",
    "AsyncPageService",
    "AsyncCategoryService", 
    "AsyncTagService",
    "AsyncUserService",
    "AsyncMediaService",
    "AsyncCommentService"
]