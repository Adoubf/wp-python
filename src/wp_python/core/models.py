"""
WordPress REST API 数据模型

基于WordPress官方文档定义的数据结构，
使用Pydantic进行数据验证和序列化。
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class PostStatus(str, Enum):
    """文章状态枚举"""
    PUBLISH = "publish"      # 已发布
    FUTURE = "future"        # 定时发布
    DRAFT = "draft"          # 草稿
    PENDING = "pending"      # 待审核
    PRIVATE = "private"      # 私密
    TRASH = "trash"          # 回收站
    AUTO_DRAFT = "auto-draft"  # 自动草稿
    INHERIT = "inherit"      # 继承


class CommentStatus(str, Enum):
    """评论状态枚举"""
    OPEN = "open"           # 开放评论
    CLOSED = "closed"       # 关闭评论


class PingStatus(str, Enum):
    """Ping状态枚举"""
    OPEN = "open"           # 开放ping
    CLOSED = "closed"       # 关闭ping


class PostFormat(str, Enum):
    """文章格式枚举"""
    STANDARD = "standard"   # 标准
    ASIDE = "aside"         # 日志
    CHAT = "chat"          # 聊天
    GALLERY = "gallery"     # 相册
    LINK = "link"          # 链接
    IMAGE = "image"        # 图片
    QUOTE = "quote"        # 引语
    STATUS = "status"      # 状态
    VIDEO = "video"        # 视频
    AUDIO = "audio"        # 音频


class BaseWordPressModel(BaseModel):
    """WordPress模型基类"""
    model_config = ConfigDict(
        extra='allow',  # 允许额外字段
        populate_by_name=True,  # 允许通过字段名填充
        str_strip_whitespace=True,  # 自动去除字符串空白
        validate_assignment=True,  # 验证赋值
        use_enum_values=True  # 使用枚举值
    )
    
    @classmethod
    def from_api_response(cls, data: Any) -> 'BaseWordPressModel':
        """
        从API响应数据创建模型实例
        
        处理WordPress API返回的各种数据格式问题
        """
        # 如果是字符串，尝试解析为JSON
        if isinstance(data, str):
            import json
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise ValueError(f"无法解析JSON字符串: {data}")
        
        if not isinstance(data, dict):
            raise ValueError(f"期望字典类型，得到: {type(data)}")
        
        # 创建数据副本以避免修改原始数据
        data = data.copy()
        
        # 处理meta字段 - WordPress有时返回空数组而不是空对象
        if 'meta' in data:
            if isinstance(data['meta'], list):
                if len(data['meta']) == 0:
                    data['meta'] = {}
                else:
                    # 如果是非空数组，尝试转换为字典
                    meta_dict = {}
                    for item in data['meta']:
                        if isinstance(item, dict) and 'key' in item and 'value' in item:
                            meta_dict[item['key']] = item['value']
                    data['meta'] = meta_dict if meta_dict else {}
            elif not isinstance(data['meta'], dict):
                data['meta'] = {}
        
        # 处理其他可能的数组/对象混淆
        for field in ['categories', 'tags']:
            if field in data and not isinstance(data[field], list):
                data[field] = []
        
        # 处理可能的None值
        for field_name, field_info in cls.model_fields.items():
            if field_name in data and data[field_name] is None:
                # 如果字段允许None，保持None；否则使用默认值
                if not field_info.is_required() and field_info.default is not None:
                    data[field_name] = field_info.default
        
        return cls(**data)


class RenderedContent(BaseWordPressModel):
    """渲染后的内容模型"""
    rendered: str = Field(description="渲染后的HTML内容")
    protected: Optional[bool] = Field(default=False, description="是否受密码保护")


class GUID(BaseWordPressModel):
    """全局唯一标识符模型"""
    rendered: str = Field(description="渲染后的GUID")


class Title(BaseWordPressModel):
    """标题模型"""
    rendered: str = Field(description="渲染后的标题")


class Excerpt(BaseWordPressModel):
    """摘要模型"""
    rendered: str = Field(description="渲染后的摘要")
    protected: Optional[bool] = Field(default=False, description="是否受密码保护")


class Post(BaseWordPressModel):
    """文章模型 - 基于WordPress官方文档"""
    
    # 基础字段
    id: Optional[int] = Field(default=None, description="文章ID")
    date: Optional[datetime] = Field(default=None, description="发布日期（站点时区）")
    date_gmt: Optional[datetime] = Field(default=None, description="发布日期（GMT时区）")
    guid: Optional[GUID] = Field(default=None, description="全局唯一标识符")
    modified: Optional[datetime] = Field(default=None, description="修改日期（站点时区）")
    modified_gmt: Optional[datetime] = Field(default=None, description="修改日期（GMT时区）")
    password: Optional[str] = Field(default="", description="文章密码")
    slug: Optional[str] = Field(default="", description="文章别名")
    status: Optional[PostStatus] = Field(default=PostStatus.DRAFT, description="文章状态")
    type: Optional[str] = Field(default="post", description="文章类型")
    link: Optional[str] = Field(default=None, description="文章链接")
    
    # 内容字段
    title: Optional[Title] = Field(default=None, description="文章标题")
    content: Optional[RenderedContent] = Field(default=None, description="文章内容")
    excerpt: Optional[Excerpt] = Field(default=None, description="文章摘要")
    
    # 作者和分类
    author: Optional[int] = Field(default=None, description="作者ID")
    featured_media: Optional[int] = Field(default=0, description="特色图片ID")
    comment_status: Optional[CommentStatus] = Field(default=CommentStatus.OPEN, description="评论状态")
    ping_status: Optional[PingStatus] = Field(default=PingStatus.OPEN, description="Ping状态")
    sticky: Optional[bool] = Field(default=False, description="是否置顶")
    template: Optional[str] = Field(default="", description="页面模板")
    format: Optional[PostFormat] = Field(default=PostFormat.STANDARD, description="文章格式")
    
    # 分类和标签
    categories: Optional[List[int]] = Field(default_factory=list, description="分类ID列表")
    tags: Optional[List[int]] = Field(default_factory=list, description="标签ID列表")
    
    # 元数据
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="自定义字段")
    
    # 嵌入数据（当使用_embed参数时）
    embedded: Optional[Dict[str, Any]] = Field(default=None, alias="_embedded", description="嵌入的相关数据")


class Page(BaseWordPressModel):
    """页面模型 - 基于WordPress官方文档"""
    
    # 基础字段
    id: Optional[int] = Field(default=None, description="页面ID")
    date: Optional[datetime] = Field(default=None, description="发布日期（站点时区）")
    date_gmt: Optional[datetime] = Field(default=None, description="发布日期（GMT时区）")
    guid: Optional[GUID] = Field(default=None, description="全局唯一标识符")
    modified: Optional[datetime] = Field(default=None, description="修改日期（站点时区）")
    modified_gmt: Optional[datetime] = Field(default=None, description="修改日期（GMT时区）")
    password: Optional[str] = Field(default="", description="页面密码")
    slug: Optional[str] = Field(default="", description="页面别名")
    status: Optional[PostStatus] = Field(default=PostStatus.DRAFT, description="页面状态")
    type: Optional[str] = Field(default="page", description="页面类型")
    link: Optional[str] = Field(default=None, description="页面链接")
    
    # 内容字段
    title: Optional[Title] = Field(default=None, description="页面标题")
    content: Optional[RenderedContent] = Field(default=None, description="页面内容")
    excerpt: Optional[Excerpt] = Field(default=None, description="页面摘要")
    
    # 页面特有字段
    author: Optional[int] = Field(default=None, description="作者ID")
    featured_media: Optional[int] = Field(default=0, description="特色图片ID")
    parent: Optional[int] = Field(default=0, description="父页面ID")
    menu_order: Optional[int] = Field(default=0, description="菜单排序")
    comment_status: Optional[CommentStatus] = Field(default=CommentStatus.CLOSED, description="评论状态")
    ping_status: Optional[PingStatus] = Field(default=PingStatus.CLOSED, description="Ping状态")
    template: Optional[str] = Field(default="", description="页面模板")
    
    # 元数据
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="自定义字段")


class Category(BaseWordPressModel):
    """分类模型"""
    
    id: Optional[int] = Field(default=None, description="分类ID")
    count: Optional[int] = Field(default=0, description="文章数量")
    description: Optional[str] = Field(default="", description="分类描述")
    link: Optional[str] = Field(default=None, description="分类链接")
    name: Optional[str] = Field(default="", description="分类名称")
    slug: Optional[str] = Field(default="", description="分类别名")
    taxonomy: Optional[str] = Field(default="category", description="分类法")
    parent: Optional[int] = Field(default=0, description="父分类ID")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="自定义字段")


class Tag(BaseWordPressModel):
    """标签模型"""
    
    id: Optional[int] = Field(default=None, description="标签ID")
    count: Optional[int] = Field(default=0, description="文章数量")
    description: Optional[str] = Field(default="", description="标签描述")
    link: Optional[str] = Field(default=None, description="标签链接")
    name: Optional[str] = Field(default="", description="标签名称")
    slug: Optional[str] = Field(default="", description="标签别名")
    taxonomy: Optional[str] = Field(default="post_tag", description="分类法")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="自定义字段")


class User(BaseWordPressModel):
    """用户模型"""
    
    id: Optional[int] = Field(default=None, description="用户ID")
    username: Optional[str] = Field(default="", description="用户名")
    name: Optional[str] = Field(default="", description="显示名称")
    first_name: Optional[str] = Field(default="", description="名字")
    last_name: Optional[str] = Field(default="", description="姓氏")
    email: Optional[str] = Field(default="", description="邮箱地址")
    url: Optional[str] = Field(default="", description="网站URL")
    description: Optional[str] = Field(default="", description="用户描述")
    link: Optional[str] = Field(default=None, description="用户链接")
    locale: Optional[str] = Field(default="", description="用户语言")
    nickname: Optional[str] = Field(default="", description="昵称")
    slug: Optional[str] = Field(default="", description="用户别名")
    registered_date: Optional[datetime] = Field(default=None, description="注册日期")
    roles: Optional[List[str]] = Field(default_factory=list, description="用户角色")
    capabilities: Optional[Dict[str, bool]] = Field(default_factory=dict, description="用户权限")
    extra_capabilities: Optional[Dict[str, bool]] = Field(default_factory=dict, description="额外权限")
    avatar_urls: Optional[Dict[str, str]] = Field(default_factory=dict, description="头像URL")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="自定义字段")


class Media(BaseWordPressModel):
    """媒体模型"""
    
    id: Optional[int] = Field(default=None, description="媒体ID")
    date: Optional[datetime] = Field(default=None, description="上传日期（站点时区）")
    date_gmt: Optional[datetime] = Field(default=None, description="上传日期（GMT时区）")
    guid: Optional[GUID] = Field(default=None, description="全局唯一标识符")
    modified: Optional[datetime] = Field(default=None, description="修改日期（站点时区）")
    modified_gmt: Optional[datetime] = Field(default=None, description="修改日期（GMT时区）")
    slug: Optional[str] = Field(default="", description="媒体别名")
    status: Optional[str] = Field(default="inherit", description="媒体状态")
    type: Optional[str] = Field(default="attachment", description="媒体类型")
    link: Optional[str] = Field(default=None, description="媒体链接")
    
    # 内容字段
    title: Optional[Title] = Field(default=None, description="媒体标题")
    author: Optional[int] = Field(default=None, description="作者ID")
    comment_status: Optional[CommentStatus] = Field(default=CommentStatus.OPEN, description="评论状态")
    ping_status: Optional[PingStatus] = Field(default=PingStatus.CLOSED, description="Ping状态")
    template: Optional[str] = Field(default="", description="模板")
    
    # 媒体特有字段
    alt_text: Optional[str] = Field(default="", description="替代文本")
    caption: Optional[RenderedContent] = Field(default=None, description="媒体说明")
    description: Optional[RenderedContent] = Field(default=None, description="媒体描述")
    media_type: Optional[str] = Field(default="", description="媒体类型")
    mime_type: Optional[str] = Field(default="", description="MIME类型")
    media_details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="媒体详情")
    post: Optional[int] = Field(default=None, description="关联文章ID")
    source_url: Optional[str] = Field(default="", description="媒体URL")
    
    # 元数据
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="自定义字段")


class Comment(BaseWordPressModel):
    """评论模型"""
    
    id: Optional[int] = Field(default=None, description="评论ID")
    post: Optional[int] = Field(default=None, description="文章ID")
    parent: Optional[int] = Field(default=0, description="父评论ID")
    author: Optional[int] = Field(default=0, description="作者ID")
    author_name: Optional[str] = Field(default="", description="作者姓名")
    author_email: Optional[str] = Field(default="", description="作者邮箱")
    author_url: Optional[str] = Field(default="", description="作者网站")
    author_ip: Optional[str] = Field(default="", description="作者IP")
    author_user_agent: Optional[str] = Field(default="", description="用户代理")
    date: Optional[datetime] = Field(default=None, description="评论日期（站点时区）")
    date_gmt: Optional[datetime] = Field(default=None, description="评论日期（GMT时区）")
    content: Optional[RenderedContent] = Field(default=None, description="评论内容")
    link: Optional[str] = Field(default=None, description="评论链接")
    status: Optional[str] = Field(default="hold", description="评论状态")
    type: Optional[str] = Field(default="comment", description="评论类型")
    author_avatar_urls: Optional[Dict[str, str]] = Field(default_factory=dict, description="作者头像URL")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="自定义字段")


# 查询参数模型
class ListQueryParams(BaseWordPressModel):
    """列表查询参数基类"""
    
    context: Optional[str] = Field(default="view", description="响应上下文")
    page: Optional[int] = Field(default=1, ge=1, description="页码")
    per_page: Optional[int] = Field(default=10, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(default=None, description="搜索关键词")
    exclude: Optional[List[int]] = Field(default=None, description="排除的ID列表")
    include: Optional[List[int]] = Field(default=None, description="包含的ID列表")
    offset: Optional[int] = Field(default=None, ge=0, description="偏移量")
    order: Optional[str] = Field(default="desc", description="排序方向")
    orderby: Optional[str] = Field(default="date", description="排序字段")


class PostQueryParams(ListQueryParams):
    """文章查询参数"""
    
    after: Optional[datetime] = Field(default=None, description="查询此日期之后的文章")
    author: Optional[List[int]] = Field(default=None, description="作者ID列表")
    author_exclude: Optional[List[int]] = Field(default=None, description="排除的作者ID列表")
    before: Optional[datetime] = Field(default=None, description="查询此日期之前的文章")
    categories: Optional[List[int]] = Field(default=None, description="分类ID列表")
    categories_exclude: Optional[List[int]] = Field(default=None, description="排除的分类ID列表")
    format: Optional[List[PostFormat]] = Field(default=None, description="文章格式列表")
    modified_after: Optional[datetime] = Field(default=None, description="查询此日期之后修改的文章")
    modified_before: Optional[datetime] = Field(default=None, description="查询此日期之前修改的文章")
    slug: Optional[List[str]] = Field(default=None, description="文章别名列表")
    status: Optional[List[PostStatus]] = Field(default=None, description="文章状态列表")
    sticky: Optional[bool] = Field(default=None, description="是否只查询置顶文章")
    tags: Optional[List[int]] = Field(default=None, description="标签ID列表")
    tags_exclude: Optional[List[int]] = Field(default=None, description="排除的标签ID列表")