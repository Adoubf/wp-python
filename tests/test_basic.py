#!/usr/bin/env python3
"""
WordPress REST API Python客户端基础测试

测试库的基本功能，包括模型创建、查询构建器、
客户端初始化等核心功能。
"""

import pytest
from datetime import datetime

from wp_python import WordPress, AsyncWordPress
from wp_python.core.models import (
    Post, Page, Category, Tag, User, Media, Comment,
    PostStatus, PostFormat, CommentStatus, PingStatus
)
from wp_python.core.exceptions import (
    WordPressError, ValidationError, AuthenticationError,
    NotFoundError, PermissionError
)
from wp_python.utils import QueryBuilder, create_query


class TestModels:
    """测试数据模型"""
    
    def test_post_model_creation(self):
        """测试文章模型创建"""
        post_data = {
            "id": 1,
            "title": {"rendered": "测试文章"},
            "content": {"rendered": "<p>测试内容</p>"},
            "status": "publish",
            "author": 1,
            "categories": [1, 2],
            "tags": [3, 4]
        }
        
        post = Post(**post_data)
        assert post.id == 1
        assert post.title.rendered == "测试文章"
        assert post.content.rendered == "<p>测试内容</p>"
        assert post.status == PostStatus.PUBLISH
        assert post.author == 1
        assert post.categories == [1, 2]
        assert post.tags == [3, 4]
    
    def test_page_model_creation(self):
        """测试页面模型创建"""
        page_data = {
            "id": 2,
            "title": {"rendered": "测试页面"},
            "content": {"rendered": "<p>页面内容</p>"},
            "parent": 0,
            "menu_order": 1
        }
        
        page = Page(**page_data)
        assert page.id == 2
        assert page.title.rendered == "测试页面"
        assert page.parent == 0
        assert page.menu_order == 1
    
    def test_category_model_creation(self):
        """测试分类模型创建"""
        category_data = {
            "id": 1,
            "name": "技术",
            "slug": "tech",
            "description": "技术相关文章",
            "count": 10,
            "parent": 0
        }
        
        category = Category(**category_data)
        assert category.id == 1
        assert category.name == "技术"
        assert category.slug == "tech"
        assert category.count == 10
        assert category.parent == 0
    
    def test_tag_model_creation(self):
        """测试标签模型创建"""
        tag_data = {
            "id": 1,
            "name": "Python",
            "slug": "python",
            "description": "Python编程",
            "count": 5
        }
        
        tag = Tag(**tag_data)
        assert tag.id == 1
        assert tag.name == "Python"
        assert tag.slug == "python"
        assert tag.count == 5
    
    def test_user_model_creation(self):
        """测试用户模型创建"""
        user_data = {
            "id": 1,
            "username": "testuser",
            "name": "测试用户",
            "email": "test@example.com",
            "roles": ["author"],
            "avatar_urls": {"96": "https://example.com/avatar.jpg"}
        }
        
        user = User(**user_data)
        assert user.id == 1
        assert user.username == "testuser"
        assert user.name == "测试用户"
        assert user.email == "test@example.com"
        assert user.roles == ["author"]
    
    def test_enums(self):
        """测试枚举类型"""
        assert PostStatus.PUBLISH == "publish"
        assert PostStatus.DRAFT == "draft"
        assert PostFormat.STANDARD == "standard"
        assert PostFormat.VIDEO == "video"
        assert CommentStatus.OPEN == "open"
        assert PingStatus.CLOSED == "closed"


class TestQueryBuilder:
    """测试查询构建器"""
    
    def test_basic_query_building(self):
        """测试基础查询构建"""
        query = (QueryBuilder()
                .page(1)
                .per_page(10)
                .search("测试")
                .order_by("date", "desc")
                .build())
        
        expected = {
            "page": 1,
            "per_page": 10,
            "search": "测试",
            "orderby": "date",
            "order": "desc"
        }
        
        assert query == expected
    
    def test_complex_query_building(self):
        """测试复杂查询构建"""
        query = (QueryBuilder()
                .per_page(20)
                .status([PostStatus.PUBLISH, PostStatus.PRIVATE])
                .categories([1, 2])
                .tags_exclude([10])
                .author([1, 2])
                .sticky(True)
                .context("edit")
                .build())
        
        assert query["per_page"] == 20
        assert query["status"] == [PostStatus.PUBLISH, PostStatus.PRIVATE]
        assert query["categories"] == [1, 2]
        assert query["tags_exclude"] == [10]
        assert query["author"] == [1, 2]
        assert query["sticky"] is True
        assert query["context"] == "edit"
    
    def test_date_queries(self):
        """测试日期查询"""
        test_date = datetime(2024, 1, 1, 12, 0, 0)
        
        query = (QueryBuilder()
                .after(test_date)
                .before(test_date)
                .build())
        
        assert query["after"] == test_date
        assert query["before"] == test_date
    
    def test_custom_parameters(self):
        """测试自定义参数"""
        query = (QueryBuilder()
                .custom("meta_key", "featured")
                .custom("meta_value", "yes")
                .build())
        
        assert query["meta_key"] == "featured"
        assert query["meta_value"] == "yes"
    
    def test_query_validation(self):
        """测试查询验证"""
        builder = QueryBuilder()
        
        # 测试无效页码
        with pytest.raises(ValueError):
            builder.page(0)
        
        # 测试无效每页数量
        with pytest.raises(ValueError):
            builder.per_page(0)
        
        with pytest.raises(ValueError):
            builder.per_page(101)
        
        # 测试无效排序方向
        with pytest.raises(ValueError):
            builder.order_by("date", "invalid")
    
    def test_create_query_function(self):
        """测试create_query函数"""
        query = (create_query()
                .page(1)
                .per_page(5)
                .build())
        
        assert isinstance(query, dict)
        assert query["page"] == 1
        assert query["per_page"] == 5
    
    def test_query_reset(self):
        """测试查询重置"""
        builder = QueryBuilder()
        builder.page(1).per_page(10)
        
        assert len(builder.build()) == 2
        
        builder.reset()
        assert len(builder.build()) == 0


class TestWordPressClient:
    """测试WordPress客户端"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        # 测试基础URL验证
        wp = WordPress("https://example.com")
        assert wp.base_url == "https://example.com"
        
        # 测试自动添加https
        wp2 = WordPress("example.com")
        assert wp2.base_url == "https://example.com"
        
        # 测试无效URL
        with pytest.raises(ValidationError):
            WordPress("")
    
    def test_client_with_auth(self):
        """测试带认证的客户端"""
        # 基础认证
        wp = WordPress(
            "https://example.com",
            username="user",
            password="pass"
        )
        assert wp.client.auth.username == "user"
        assert wp.client.auth.password == "pass"
        
        # 应用程序密码
        wp2 = WordPress(
            "https://example.com",
            username="user",
            app_password="app_pass"
        )
        assert wp2.client.auth.username == "user"
        assert wp2.client.auth.app_password == "app_pass"
        
        # JWT令牌
        wp3 = WordPress(
            "https://example.com",
            jwt_token="jwt_token"
        )
        assert wp3.client.auth.jwt_token == "jwt_token"
    
    def test_service_initialization(self):
        """测试服务初始化"""
        wp = WordPress("https://example.com")
        
        # 检查所有服务是否正确初始化
        assert hasattr(wp, 'posts')
        assert hasattr(wp, 'pages')
        assert hasattr(wp, 'categories')
        assert hasattr(wp, 'tags')
        assert hasattr(wp, 'users')
        assert hasattr(wp, 'media')
        assert hasattr(wp, 'comments')
        
        # 检查服务类型
        from wp_python.service.posts import PostService
        from wp_python.service.pages import PageService
        from wp_python.service.categories import CategoryService
        
        assert isinstance(wp.posts, PostService)
        assert isinstance(wp.pages, PageService)
        assert isinstance(wp.categories, CategoryService)
    
    def test_async_client_initialization(self):
        """测试异步客户端初始化"""
        wp = AsyncWordPress("https://example.com")
        assert wp.base_url == "https://example.com"
        
        # 检查异步服务
        from wp_python.service.posts import AsyncPostService
        assert isinstance(wp.posts, AsyncPostService)


class TestExceptions:
    """测试异常处理"""
    
    def test_exception_hierarchy(self):
        """测试异常层次结构"""
        # 所有异常都应该继承自WordPressError
        assert issubclass(AuthenticationError, WordPressError)
        assert issubclass(ValidationError, WordPressError)
        assert issubclass(NotFoundError, WordPressError)
        assert issubclass(PermissionError, WordPressError)
    
    def test_exception_creation(self):
        """测试异常创建"""
        error = WordPressError(
            message="测试错误",
            code="test_error",
            status_code=400,
            data={"field": "value"}
        )
        
        assert str(error) == "[test_error] HTTP 400 测试错误"
        assert error.message == "测试错误"
        assert error.code == "test_error"
        assert error.status_code == 400
        assert error.data == {"field": "value"}
    
    def test_exception_from_response(self):
        """测试从响应创建异常"""
        from wp_python.core.exceptions import create_exception_from_response
        
        # 401错误应该创建AuthenticationError
        auth_error = create_exception_from_response(
            401,
            {"message": "未认证", "code": "rest_not_logged_in"}
        )
        assert isinstance(auth_error, AuthenticationError)
        
        # 404错误应该创建NotFoundError
        not_found_error = create_exception_from_response(
            404,
            {"message": "未找到", "code": "rest_post_invalid_id"}
        )
        assert isinstance(not_found_error, NotFoundError)


def test_package_imports():
    """测试包导入"""
    # 测试主包导入
    from wp_python import WordPress, AsyncWordPress
    assert WordPress is not None
    assert AsyncWordPress is not None
    
    # 测试异常导入
    from wp_python import (
        WordPressError, AuthenticationError, NotFoundError,
        ValidationError, PermissionError, RateLimitError
    )
    
    # 测试模型导入
    from wp_python.core.models import Post, Page, Category, Tag
    
    # 测试工具导入
    from wp_python.utils import QueryBuilder, create_query


def test_version_info():
    """测试版本信息"""
    import wp_python
    assert hasattr(wp_python, '__version__')
    assert hasattr(wp_python, '__author__')
    assert wp_python.__version__ == "0.2.0"


if __name__ == "__main__":
    # 运行基础测试
    print("运行WordPress REST API Python客户端基础测试...")
    
    # 测试模型创建
    test_models = TestModels()
    test_models.test_post_model_creation()
    test_models.test_category_model_creation()
    test_models.test_enums()
    print("✓ 模型测试通过")
    
    # 测试查询构建器
    test_query = TestQueryBuilder()
    test_query.test_basic_query_building()
    test_query.test_complex_query_building()
    test_query.test_create_query_function()
    print("✓ 查询构建器测试通过")
    
    # 测试客户端初始化
    test_client = TestWordPressClient()
    test_client.test_client_initialization()
    test_client.test_service_initialization()
    print("✓ 客户端测试通过")
    
    # 测试异常
    test_exceptions = TestExceptions()
    test_exceptions.test_exception_hierarchy()
    test_exceptions.test_exception_creation()
    print("✓ 异常测试通过")
    
    # 测试导入
    test_package_imports()
    test_version_info()
    print("✓ 包导入测试通过")
    
    print("\n所有基础测试通过！✅")
    print("要运行完整测试，请使用: poetry run python -m pytest tests/")