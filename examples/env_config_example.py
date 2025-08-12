#!/usr/bin/env python3
"""
WordPress REST API Python客户端环境配置示例

演示如何使用.env.dev文件配置和日志系统。
"""

from wp_python import WordPress
from wp_python.utils import get_config, setup_logging
from wp_python.core.models import PostStatus


def main():
    """主函数 - 使用环境配置"""
    print("=== WordPress REST API 环境配置示例 ===\n")
    
    # 1. 加载配置
    print("1. 加载环境配置...")
    config = get_config()
    
    print("配置信息:")
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        if 'password' in key.lower() or 'token' in key.lower():
            # 隐藏敏感信息
            display_value = "***已配置***" if value else "未配置"
        else:
            display_value = value
        print(f"  {key}: {display_value}")
    
    # 2. 设置日志
    print(f"\n2. 设置日志系统...")
    logger = setup_logging(
        level=config.log_level,
        log_file=config.log_file,
        console_output=True
    )
    
    logger.info("日志系统初始化完成")
    logger.success("环境配置加载成功")
    
    # 3. 创建WordPress客户端
    print("\n3. 创建WordPress客户端...")
    
    try:
        wp = WordPress(
            config.base_url,
            **config.get_auth_config(),
            **config.get_client_config()
        )
        
        logger.success(f"WordPress客户端创建成功: {config.base_url}")
        
        # 4. 测试连接
        print("\n4. 测试连接...")
        logger.progress("正在测试连接...")
        
        connection_info = wp.test_connection()
        logger.success(f"连接成功: {connection_info['status']}")
        print(f"API地址: {connection_info['api_url']}")
        
        # 5. 获取站点信息
        print("\n5. 获取站点信息...")
        logger.progress("正在获取站点信息...")
        
        site_info = wp.get_site_info()
        
        # WordPress REST API根端点可能返回不同的字段
        site_name = (site_info.get('name') or 
                    site_info.get('title') or 
                    site_info.get('site_title') or '未知')
        
        site_desc = (site_info.get('description') or 
                    site_info.get('tagline') or 
                    site_info.get('site_tagline') or '未知')
        
        site_url = (site_info.get('url') or 
                   site_info.get('home') or 
                   site_info.get('site_url') or '未知')
        
        logger.info(f"站点名称: {site_name}")
        logger.info(f"站点描述: {site_desc}")
        logger.info(f"站点URL: {site_url}")
        logger.info(f"API版本: {site_info.get('namespaces', '未知')}")
        
        # 6. 测试文章操作
        print("\n6. 测试文章操作...")
        logger.progress("正在获取文章列表...")
        
        # 使用枚举和字符串混合
        posts = wp.posts.list(
            per_page=3,
            status=[PostStatus.PUBLISH, 'draft'],  # 混合使用
            order='desc'
        )
        
        logger.success(f"获取到 {len(posts)} 篇文章")
        for post in posts:
            logger.info(f"文章: {post.title.rendered} (状态: {post.status})")
        
        # 7. 测试分类操作
        print("\n7. 测试分类操作...")
        logger.progress("正在获取分类列表...")
        
        categories = wp.categories.list(per_page=5)
        logger.success(f"获取到 {len(categories)} 个分类")
        
        for category in categories:
            logger.info(f"分类: {category.name} (文章数: {category.count})")
        
        # 8. 测试用户操作
        print("\n8. 测试用户操作...")
        logger.progress("正在获取当前用户信息...")
        
        try:
            current_user = wp.users.get_me()
            logger.success(f"当前用户: {current_user.name} ({current_user.email})")
            logger.info(f"用户角色: {current_user.roles}")
        except Exception as e:
            logger.warning(f"获取用户信息失败: {e}")
        
        print("\n=== 环境配置示例完成 ===")
        logger.success("所有测试完成")
        
    except Exception as e:
        logger.failure(f"操作失败: {e}")
        print(f"\n错误详情: {e}")
        
        # 如果是WordPress错误，显示详细信息
        if hasattr(e, 'to_dict'):
            error_dict = e.to_dict()
            print("错误信息:")
            for key, value in error_dict.items():
                if value is not None:
                    print(f"  {key}: {value}")
    
    finally:
        if 'wp' in locals():
            wp.close()
            logger.info("WordPress客户端已关闭")


if __name__ == "__main__":
    main()