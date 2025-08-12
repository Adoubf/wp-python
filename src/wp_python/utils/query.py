"""
WordPress REST API 查询构建器

提供便捷的查询参数构建功能，
帮助用户更容易地构建复杂的API查询。
"""

from typing import Dict, Any, List, Union
from datetime import datetime

from ..core.models import PostStatus, PostFormat


class QueryBuilder:
    """
    WordPress REST API 查询构建器
    
    提供链式调用的方式来构建查询参数，
    使API查询更加直观和易用。
    
    使用示例:
        query = QueryBuilder()
        params = (query
                 .page(1)
                 .per_page(10)
                 .search("关键词")
                 .status([PostStatus.PUBLISH])
                 .order_by("date", "desc")
                 .build())
    """
    
    def __init__(self):
        """初始化查询构建器"""
        self._params: Dict[str, Any] = {}
    
    def page(self, page_num: int) -> 'QueryBuilder':
        """
        设置页码
        
        参数:
            page_num: 页码，从1开始
            
        返回:
            查询构建器实例（支持链式调用）
        """
        if page_num < 1:
            raise ValueError("页码必须大于0")
        self._params["page"] = page_num
        return self
    
    def per_page(self, count: int) -> 'QueryBuilder':
        """
        设置每页数量
        
        参数:
            count: 每页数量，最大100
            
        返回:
            查询构建器实例
        """
        if count < 1 or count > 100:
            raise ValueError("每页数量必须在1-100之间")
        self._params["per_page"] = count
        return self
    
    def search(self, keyword: str) -> 'QueryBuilder':
        """
        设置搜索关键词
        
        参数:
            keyword: 搜索关键词
            
        返回:
            查询构建器实例
        """
        if keyword:
            self._params["search"] = keyword
        return self
    
    def include(self, ids: List[int]) -> 'QueryBuilder':
        """
        包含指定ID的项目
        
        参数:
            ids: ID列表
            
        返回:
            查询构建器实例
        """
        if ids:
            self._params["include"] = ids
        return self
    
    def exclude(self, ids: List[int]) -> 'QueryBuilder':
        """
        排除指定ID的项目
        
        参数:
            ids: ID列表
            
        返回:
            查询构建器实例
        """
        if ids:
            self._params["exclude"] = ids
        return self
    
    def order_by(self, field: str, direction: str = "desc") -> 'QueryBuilder':
        """
        设置排序
        
        参数:
            field: 排序字段
            direction: 排序方向 (asc/desc)
            
        返回:
            查询构建器实例
        """
        if direction not in ["asc", "desc"]:
            raise ValueError("排序方向必须是 'asc' 或 'desc'")
        
        self._params["orderby"] = field
        self._params["order"] = direction
        return self
    
    def offset(self, offset_count: int) -> 'QueryBuilder':
        """
        设置偏移量
        
        参数:
            offset_count: 偏移量
            
        返回:
            查询构建器实例
        """
        if offset_count >= 0:
            self._params["offset"] = offset_count
        return self
    
    def context(self, ctx: str) -> 'QueryBuilder':
        """
        设置响应上下文
        
        参数:
            ctx: 上下文 (view/embed/edit)
            
        返回:
            查询构建器实例
        """
        if ctx in ["view", "embed", "edit"]:
            self._params["context"] = ctx
        return self
    
    def status(self, statuses: Union[PostStatus, List[PostStatus]]) -> 'QueryBuilder':
        """
        设置文章状态过滤
        
        参数:
            statuses: 状态或状态列表
            
        返回:
            查询构建器实例
        """
        if isinstance(statuses, PostStatus):
            statuses = [statuses]
        
        if statuses:
            self._params["status"] = statuses
        return self
    
    def author(self, author_ids: Union[int, List[int]]) -> 'QueryBuilder':
        """
        设置作者过滤
        
        参数:
            author_ids: 作者ID或ID列表
            
        返回:
            查询构建器实例
        """
        if isinstance(author_ids, int):
            author_ids = [author_ids]
        
        if author_ids:
            self._params["author"] = author_ids
        return self
    
    def author_exclude(self, author_ids: Union[int, List[int]]) -> 'QueryBuilder':
        """
        排除指定作者
        
        参数:
            author_ids: 作者ID或ID列表
            
        返回:
            查询构建器实例
        """
        if isinstance(author_ids, int):
            author_ids = [author_ids]
        
        if author_ids:
            self._params["author_exclude"] = author_ids
        return self
    
    def categories(self, category_ids: Union[int, List[int]]) -> 'QueryBuilder':
        """
        设置分类过滤
        
        参数:
            category_ids: 分类ID或ID列表
            
        返回:
            查询构建器实例
        """
        if isinstance(category_ids, int):
            category_ids = [category_ids]
        
        if category_ids:
            self._params["categories"] = category_ids
        return self
    
    def categories_exclude(self, category_ids: Union[int, List[int]]) -> 'QueryBuilder':
        """
        排除指定分类
        
        参数:
            category_ids: 分类ID或ID列表
            
        返回:
            查询构建器实例
        """
        if isinstance(category_ids, int):
            category_ids = [category_ids]
        
        if category_ids:
            self._params["categories_exclude"] = category_ids
        return self
    
    def tags(self, tag_ids: Union[int, List[int]]) -> 'QueryBuilder':
        """
        设置标签过滤
        
        参数:
            tag_ids: 标签ID或ID列表
            
        返回:
            查询构建器实例
        """
        if isinstance(tag_ids, int):
            tag_ids = [tag_ids]
        
        if tag_ids:
            self._params["tags"] = tag_ids
        return self
    
    def tags_exclude(self, tag_ids: Union[int, List[int]]) -> 'QueryBuilder':
        """
        排除指定标签
        
        参数:
            tag_ids: 标签ID或ID列表
            
        返回:
            查询构建器实例
        """
        if isinstance(tag_ids, int):
            tag_ids = [tag_ids]
        
        if tag_ids:
            self._params["tags_exclude"] = tag_ids
        return self
    
    def after(self, date: datetime) -> 'QueryBuilder':
        """
        查询指定日期之后的内容
        
        参数:
            date: 日期时间
            
        返回:
            查询构建器实例
        """
        self._params["after"] = date
        return self
    
    def before(self, date: datetime) -> 'QueryBuilder':
        """
        查询指定日期之前的内容
        
        参数:
            date: 日期时间
            
        返回:
            查询构建器实例
        """
        self._params["before"] = date
        return self
    
    def modified_after(self, date: datetime) -> 'QueryBuilder':
        """
        查询指定日期之后修改的内容
        
        参数:
            date: 日期时间
            
        返回:
            查询构建器实例
        """
        self._params["modified_after"] = date
        return self
    
    def modified_before(self, date: datetime) -> 'QueryBuilder':
        """
        查询指定日期之前修改的内容
        
        参数:
            date: 日期时间
            
        返回:
            查询构建器实例
        """
        self._params["modified_before"] = date
        return self
    
    def slug(self, slugs: Union[str, List[str]]) -> 'QueryBuilder':
        """
        设置别名过滤
        
        参数:
            slugs: 别名或别名列表
            
        返回:
            查询构建器实例
        """
        if isinstance(slugs, str):
            slugs = [slugs]
        
        if slugs:
            self._params["slug"] = slugs
        return self
    
    def sticky(self, is_sticky: bool) -> 'QueryBuilder':
        """
        设置置顶文章过滤
        
        参数:
            is_sticky: 是否只查询置顶文章
            
        返回:
            查询构建器实例
        """
        self._params["sticky"] = is_sticky
        return self
    
    def format(self, formats: Union[PostFormat, List[PostFormat]]) -> 'QueryBuilder':
        """
        设置文章格式过滤
        
        参数:
            formats: 格式或格式列表
            
        返回:
            查询构建器实例
        """
        if isinstance(formats, PostFormat):
            formats = [formats]
        
        if formats:
            self._params["format"] = formats
        return self
    
    def parent(self, parent_ids: Union[int, List[int]]) -> 'QueryBuilder':
        """
        设置父级过滤（用于页面和分类）
        
        参数:
            parent_ids: 父级ID或ID列表
            
        返回:
            查询构建器实例
        """
        if isinstance(parent_ids, int):
            parent_ids = [parent_ids]
        
        if parent_ids:
            self._params["parent"] = parent_ids
        return self
    
    def parent_exclude(self, parent_ids: Union[int, List[int]]) -> 'QueryBuilder':
        """
        排除指定父级
        
        参数:
            parent_ids: 父级ID或ID列表
            
        返回:
            查询构建器实例
        """
        if isinstance(parent_ids, int):
            parent_ids = [parent_ids]
        
        if parent_ids:
            self._params["parent_exclude"] = parent_ids
        return self
    
    def hide_empty(self, hide: bool) -> 'QueryBuilder':
        """
        设置是否隐藏空分类/标签
        
        参数:
            hide: 是否隐藏空项目
            
        返回:
            查询构建器实例
        """
        self._params["hide_empty"] = hide
        return self
    
    def custom(self, key: str, value: Any) -> 'QueryBuilder':
        """
        添加自定义查询参数
        
        参数:
            key: 参数名
            value: 参数值
            
        返回:
            查询构建器实例
        """
        self._params[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        构建最终的查询参数字典
        
        返回:
            查询参数字典
        """
        return self._params.copy()
    
    def reset(self) -> 'QueryBuilder':
        """
        重置查询构建器
        
        返回:
            查询构建器实例
        """
        self._params.clear()
        return self
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"QueryBuilder(params={self._params})"


def create_query() -> QueryBuilder:
    """
    创建新的查询构建器实例
    
    返回:
        查询构建器实例
    """
    return QueryBuilder()