#!/usr/bin/env python3
"""
WordPress REST API Python客户端基础使用示例

演示如何使用wp-python库进行基本的WordPress操作，
包括文章、页面、分类、标签等的CRUD操作。
"""

import asyncio
from datetime import datetime
from wp_python import WordPress, AsyncWordPress
from wp_python.core.models import PostStatus, PostFormat
from wp_python.utils import create_query
from wp_python.utils.config import get_config


config = get_config(".env.dev")
print(config.to_dict())

def sync_examples():
    """同步操作示例"""
    print("=== WordPress REST API Python客户端 - 同步操作示例 ===\n")
    
    # 创建WordPress客户端实例
    # 注意：请替换为您的实际WordPress站点URL和认证信息
    wp = WordPress(
        config.base_url,
        username=config.username,
        app_password=config.app_password,
        
        # 或使用基础认证（仅用于开发测试）
        # username='your-username',
        # password='your-password'
        
        # 或使用JWT令牌（需要JWT插件）
        # jwt_token='your-jwt-token'
        
        # 或无认证（只读访问）
        # 不提供认证参数
    )
    
    try:
        # 1. 测试连接
        print("1. 测试连接...")
        connection_info = wp.test_connection()
        print(f"连接状态: {connection_info['status']}")
        print(f"API地址: {connection_info['api_url']}\n")
        
        # 2. 获取站点信息
        print("2. 获取站点信息...")
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
        
        print(f"站点名称: {site_name}")
        print(f"站点描述: {site_desc}")
        print(f"站点URL: {site_url}")
        print(f"API命名空间: {site_info.get('namespaces', '未知')}")
        print(f"认证方式: {site_info.get('authentication', '未知')}\n")
        
        # 3. 文章操作示例
        print("3. 文章操作示例...")
        
        # 获取文章列表
        print("获取最新的5篇已发布文章:")
        posts = wp.posts.list(
            per_page=5,
            status=[PostStatus.PUBLISH],
            order="desc",
            orderby="date"
        )
        
        for post in posts:
            print(f"- {post.title.rendered if post.title else '无标题'} (ID: {post.id})")
        
        # 使用查询构建器
        print("\n使用查询构建器获取文章:")
        query = (create_query()
                .per_page(3)
                .status([PostStatus.PUBLISH])
                .order_by("date", "desc")
                .categories([1])  # 假设分类ID为1
                .build())
        
        posts_with_query = wp.posts.list(**query)
        for post in posts_with_query:
            print(f"- {post.title.rendered if post.title else '无标题'}")
        
        # 创建新文章（需要适当权限）
        print("\n创建新文章:")
        try:
            new_post = wp.posts.create(
                title="测试文章标题",
                content="<p>这是一篇通过Python API创建的测试文章。</p>",
                status=PostStatus.DRAFT,  # 创建为草稿
                excerpt="这是文章摘要",
                format=PostFormat.STANDARD
            )
            print(f"成功创建文章: {new_post.title.rendered} (ID: {new_post.id})")
            
            # 更新文章
            updated_post = wp.posts.update(
                new_post.id,
                title="更新后的文章标题",
                content="<p>这是更新后的文章内容。</p>"
            )
            print(f"成功更新文章: {updated_post.title.rendered}")
            
        except Exception as e:
            print(f"文章操作失败（可能是权限问题）: {e}")
        
        # 4. 分类操作示例
        print("\n4. 分类操作示例...")
        categories = wp.categories.list(per_page=5)
        print("前5个分类:")
        for category in categories:
            print(f"- {category.name} (ID: {category.id}, 文章数: {category.count})")
        
        # 5. 标签操作示例
        print("\n5. 标签操作示例...")
        tags = wp.tags.list(per_page=5)
        print("前5个标签:")
        for tag in tags:
            print(f"- {tag.name} (ID: {tag.id}, 文章数: {tag.count})")
        
        # 6. 用户操作示例
        print("\n6. 用户操作示例...")
        try:
            users = wp.users.list(per_page=3)
            print("前3个用户:")
            for user in users:
                print(f"- {user.name} ({user.username})")
        except Exception as e:
            print(f"获取用户列表失败（可能是权限问题）: {e}")
        
        # 7. 页面操作示例
        print("\n7. 页面操作示例...")
        pages = wp.pages.list(per_page=3)
        print("前3个页面:")
        for page in pages:
            print(f"- {page.title.rendered if page.title else '无标题'} (ID: {page.id})")
        
        print("\n=== 同步操作示例完成 ===\n")
        
    except Exception as e:
        print(f"操作失败: {e}")
    
    finally:
        # 关闭连接
        wp.close()


async def async_examples():
    """异步操作示例"""
    print("=== WordPress REST API Python客户端 - 异步操作示例 ===\n")
    
    # 从环境配置创建异步客户端
    from wp_python.utils import get_config
    
    config = get_config()
    async with AsyncWordPress(
        config.base_url,
        **config.get_auth_config(),
        **config.get_client_config()
    ) as wp:
        
        try:
            # 1. 异步测试连接
            print("1. 异步测试连接...")
            connection_info = await wp.test_connection()
            print(f"连接状态: {connection_info['status']}")
            
            # 2. 并发获取多种内容
            print("\n2. 并发获取内容...")
            
            # 同时获取文章、页面和分类
            posts_task = wp.posts.list(per_page=3)
            pages_task = wp.pages.list(per_page=3)
            categories_task = wp.categories.list(per_page=3)
            
            # 等待所有任务完成
            posts, pages, categories = await asyncio.gather(
                posts_task,
                pages_task,
                categories_task
            )
            
            print(f"获取到 {len(posts)} 篇文章")
            print(f"获取到 {len(pages)} 个页面")
            print(f"获取到 {len(categories)} 个分类")
            
            # 3. 异步创建内容
            print("\n3. 异步创建内容...")
            try:
                new_post = await wp.posts.create(
                    title="异步创建的文章",
                    content="<p>这是通过异步API创建的文章。</p>",
                    status=PostStatus.DRAFT
                )
                print(f"异步创建文章成功: {new_post.title.rendered}")
                
            except Exception as e:
                print(f"异步创建文章失败: {e}")
            
            print("\n=== 异步操作示例完成 ===\n")
            
        except Exception as e:
            print(f"异步操作失败: {e}")


def query_builder_examples():
    """查询构建器使用示例"""
    print("=== 查询构建器使用示例 ===\n")
    
    # 1. 基础查询
    print("1. 基础查询构建:")
    query = (create_query()
             .page(1)
             .per_page(10)
             .search("WordPress")
             .order_by("date", "desc")
             .build())
    print(f"查询参数: {query}")
    
    # 2. 复杂查询
    print("\n2. 复杂查询构建:")
    complex_query = (create_query()
                    .per_page(20)
                    .status([PostStatus.PUBLISH, PostStatus.PRIVATE])
                    .categories([1, 2, 3])
                    .tags_exclude([10, 11])
                    .after(datetime(2024, 1, 1))
                    .sticky(True)
                    .format([PostFormat.STANDARD, PostFormat.VIDEO])
                    .context("edit")
                    .build())
    print(f"复杂查询参数: {complex_query}")
    
    # 3. 自定义参数
    print("\n3. 自定义参数:")
    custom_query = (create_query()
                   .per_page(5)
                   .custom("meta_key", "featured")
                   .custom("meta_value", "yes")
                   .build())
    print(f"自定义查询参数: {custom_query}")
    
    print("\n=== 查询构建器示例完成 ===\n")


def main():
    """主函数"""
    print("WordPress REST API Python客户端使用示例\n")
    print("注意: 请在运行前修改WordPress站点URL和认证信息\n")
    
    # 查询构建器示例（不需要实际连接）
    query_builder_examples()
    
    # 同步操作示例
    # 注意：需要修改WordPress站点信息才能运行
    print("要运行实际的API操作示例，请:")
    print("1. 修改WordPress站点URL")
    print("2. 配置正确的认证信息")
    print("3. 取消下面代码的注释\n")
    
    sync_examples()
    
    # 异步操作示例
    asyncio.run(async_examples())


if __name__ == "__main__":
    main()