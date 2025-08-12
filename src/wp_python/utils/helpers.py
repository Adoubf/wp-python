"""
WordPress REST API 辅助工具函数

提供通用的辅助函数，用于处理API参数转换、数据格式化等。
"""

from typing import List, Union, Any


def convert_enum_or_string_list(items: List[Union[Any, str]]) -> List[str]:
    """
    将枚举或字符串列表转换为字符串列表
    
    支持枚举类型和字符串类型的混合使用，提供更好的用户体验。
    
    参数:
        items: 包含枚举或字符串的列表
        
    返回:
        字符串列表
        
    示例:
        >>> from wp_python.core.models import PostStatus
        >>> convert_enum_or_string_list([PostStatus.PUBLISH, "draft"])
        ['publish', 'draft']
    """
    result = []
    for item in items:
        if hasattr(item, 'value'):  # 枚举类型
            result.append(item.value)
        else:  # 字符串或其他类型
            result.append(str(item))
    return result


def convert_single_enum_or_string(item: Union[Any, str]) -> str:
    """
    将单个枚举或字符串转换为字符串
    
    参数:
        item: 枚举或字符串
        
    返回:
        字符串值
    """
    if hasattr(item, 'value'):  # 枚举类型
        return item.value
    else:  # 字符串或其他类型
        return str(item)


def build_comma_separated_param(items: List[Union[Any, str]]) -> str:
    """
    构建逗号分隔的参数字符串
    
    参数:
        items: 项目列表（可以是枚举或字符串）
        
    返回:
        逗号分隔的字符串
    """
    return ",".join(convert_enum_or_string_list(items))


def safe_build_params(**kwargs) -> dict:
    """
    安全地构建查询参数，自动处理枚举转换
    
    参数:
        **kwargs: 查询参数
        
    返回:
        处理后的参数字典
    """
    params = {}
    
    for key, value in kwargs.items():
        if value is None:
            continue
            
        if isinstance(value, list):
            if value:  # 非空列表
                if hasattr(value[0], 'value'):  # 枚举列表
                    params[key] = build_comma_separated_param(value)
                else:  # 普通列表
                    params[key] = ",".join(map(str, value))
        elif hasattr(value, 'value'):  # 单个枚举
            params[key] = value.value
        else:  # 其他类型
            params[key] = value
    
    return params