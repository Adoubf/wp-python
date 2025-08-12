#!/usr/bin/env python3
"""
WordPress REST API Python客户端高级使用示例

演示高级功能和最佳实践，包括：
- 枚举和字符串混合使用
- 复杂查询构建
- 异步批量操作
- 错误处理
- 文件上传
- 自定义字段管理
"""

import asyncio
from datetime import datetime, timedelta
from wp_python import WordPress, AsyncWordPress
from wp_python.core.models import PostStatus, PostFormat
from wp_python.core.exceptions import WordPressError, NotFoundError, ValidationError
from wp_python.utils import create_query


def demo_enum_string_compatibility():
    """演示枚举和字符串的兼容性使用"""
    print("=== 枚举和字符串兼容性演示 ===\n")
    
    # 注意：这里使用示例URL，实际使用时请替换
    wp = WordPress("https://coralera.org")
    
    try:
        # 1. 纯字符串使用（传统方式）
        print("1. 使用纯字符串参数:")
        print("   wp.posts.list(status=['publish', 'draft'])")
        
        # 2. 纯枚举使用（类型安全）
        print("2. 使用纯枚举参数:")
        print("   wp.posts.list(status=[PostStatus.PUBLISH, PostStatus.DRAFT])")
        
        # 3. 混合使用（灵活性）
        print("3. 混合使用枚举和字符串:")
        print("   wp.posts.list(status=[PostStatus.PUBLISH, 'draft'])")
        print("   wp.posts.list(format=['standard', PostFormat.VIDEO])")
        
        print("✓ 所有方式都被支持，提供最大的灵活性！\n")
        
    except Exception as e:
        print(f"演示失败: {e}\n")
    
    finally:
        wp.close()


def demo_advanced_queries():
    """演示高级查询功能"""
    print("=== 高级查询功能演示 ===\n")
    
    wp = WordPress("https://coralera.org")
    
    try:
        # 1. 使用查询构建器创建复杂查询
        print("1. 复杂查询构建器:")
        
        # 查询最近30天内发布的技术文章，排除特定标签
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        query = (create_query()
                .per_page(20)
                .status([PostStatus.PUBLISH])  # 只要已发布的
                .categories([1, 2])  # 技术分类
                .tags_exclude([99])  # 排除"草稿"标签
                .after(thirty_days_ago)  # 最近30天
                .format([PostFormat.STANDARD, PostFormat.VIDEO])  # 标准和视频格式
                .order_by("date", "desc")  # 按日期降序
                .sticky(False)  # 排除置顶文章
                .context("view")
                .build())
        
        print(f"   构建的查询参数: {query}")
        
        # 2. 分页查询示例
        print("\n2. 分页查询:")
        page_query = (create_query()
                     .page(2)  # 第二页
                     .per_page(10)  # 每页10条
                     .status(['publish'])
                     .order_by("modified", "desc")  # 按修改时间排序
                     .build())
        
        print(f"   分页查询参数: {page_query}")
        
        # 3. 搜索查询
        print("\n3. 搜索查询:")
        search_query = (create_query()
                       .search("Python WordPress")  # 搜索关键词
                       .per_page(5)
                       .status([PostStatus.PUBLISH])
                       .order_by("relevance", "desc")  # 按相关性排序
                       .build())
        
        print(f"   搜索查询参数: {search_query}")
        
        # 4. 作者和分类过滤
        print("\n4. 作者和分类过滤:")
        author_query = (create_query()
                       .author([1, 2, 3])  # 特定作者
                       .categories([5])  # 特定分类
                       .tags([10, 11])  # 特定标签
                       .per_page(15)
                       .build())
        
        print(f"   作者分类查询参数: {author_query}")
        
        print("✓ 查询构建器提供了强大而灵活的查询能力！\n")
        
    except Exception as e:
        print(f"查询演示失败: {e}\n")
    
    finally:
        wp.close()


async def demo_async_batch_operations():
    """演示异步批量操作"""
    print("=== 异步批量操作演示 ===\n")
    
    async with AsyncWordPress("https://coralera.org") as wp:
        try:
            # 1. 并发获取不同类型的内容
            print("1. 并发获取多种内容:")
            
            # 同时发起多个请求
            posts_task = wp.posts.list(per_page=5, status=['publish'])
            pages_task = wp.pages.list(per_page=3)
            categories_task = wp.categories.list(per_page=10)
            tags_task = wp.tags.list(per_page=10)
            
            # 等待所有请求完成
            posts, pages, categories, tags = await asyncio.gather(
                posts_task, pages_task, categories_task, tags_task,
                return_exceptions=True  # 即使某个请求失败也继续
            )
            
            print(f"   获取到 {len(posts) if isinstance(posts, list) else 0} 篇文章")
            print(f"   获取到 {len(pages) if isinstance(pages, list) else 0} 个页面")
            print(f"   获取到 {len(categories) if isinstance(categories, list) else 0} 个分类")
            print(f"   获取到 {len(tags) if isinstance(tags, list) else 0} 个标签")
            
            # 2. 批量创建内容
            print("\n2. 批量创建文章:")
            
            create_tasks = []
            for i in range(3):
                task = wp.posts.create(
                    title=f"批量创建的文章 {i+1}",
                    content=f"<p>这是第 {i+1} 篇批量创建的文章内容。</p>",
                    status=PostStatus.DRAFT,  # 创建为草稿
                    excerpt=f"文章 {i+1} 的摘要"
                )
                create_tasks.append(task)
            
            # 并发创建（注意：实际使用时要考虑API限制）
            created_posts = await asyncio.gather(*create_tasks, return_exceptions=True)
            
            success_count = sum(1 for post in created_posts if not isinstance(post, Exception))
            print(f"   成功创建 {success_count} 篇文章")
            
            # 3. 批量更新
            print("\n3. 批量更新文章:")
            
            if success_count > 0:
                update_tasks = []
                for i, post in enumerate(created_posts):
                    if not isinstance(post, Exception):
                        task = wp.posts.update(
                            post.id,
                            title=f"更新后的文章标题 {i+1}",
                            content=f"<p>这是更新后的文章内容 {i+1}。</p>"
                        )
                        update_tasks.append(task)
                
                updated_posts = await asyncio.gather(*update_tasks, return_exceptions=True)
                update_success = sum(1 for post in updated_posts if not isinstance(post, Exception))
                print(f"   成功更新 {update_success} 篇文章")
            
            print("✓ 异步批量操作完成！\n")
            
        except Exception as e:
            print(f"异步操作演示失败: {e}\n")


def demo_error_handling():
    """演示错误处理最佳实践"""
    print("=== 错误处理演示 ===\n")
    
    wp = WordPress("https://coralera.org")
    
    try:
        # 1. 基础错误处理
        print("1. 基础错误处理:")
        
        try:
            # 尝试获取不存在的文章
            post = wp.posts.get(999999)
        except NotFoundError as e:
            print(f"   ✓ 捕获到NotFoundError: {e}")
        except WordPressError as e:
            print(f"   ✓ 捕获到WordPressError: {e}")
        
        # 2. 验证错误处理
        print("\n2. 验证错误处理:")
        
        try:
            # 尝试创建无效的文章
            invalid_post = wp.posts.create(
                title="",  # 空标题可能导致验证错误
                content="",
                status="invalid_status"  # 无效状态
            )
        except ValidationError as e:
            print(f"   ✓ 捕获到ValidationError: {e}")
        except WordPressError as e:
            print(f"   ✓ 捕获到WordPressError: {e}")
        
        # 3. 网络错误处理
        print("\n3. 网络错误处理:")
        
        try:
            # 使用无效的URL测试网络错误
            invalid_wp = WordPress("https://invalid-domain-12345.com")
            posts = invalid_wp.posts.list()
        except Exception as e:
            print(f"   ✓ 捕获到网络错误: {type(e).__name__}: {e}")
        
        # 4. 权限错误处理
        print("\n4. 权限错误处理:")
        print("   (需要实际的WordPress站点来演示权限错误)")
        
        print("✓ 错误处理演示完成！\n")
        
    except Exception as e:
        print(f"错误处理演示失败: {e}\n")
    
    finally:
        wp.close()


def demo_media_upload():
    """演示媒体文件上传"""
    print("=== 媒体文件上传演示 ===\n")
    
    wp = WordPress("https://coralera.org")
    
    try:
        # 1. 从文件路径上传
        print("1. 从文件路径上传:")
        print("   # 假设有一个图片文件")
        print("   media = wp.media.upload(")
        print("       file_path='path/to/image.jpg',")
        print("       title='上传的图片',")
        print("       alt_text='图片描述',")
        print("       caption='图片说明'")
        print("   )")
        
        # 2. 从字节数据上传
        print("\n2. 从字节数据上传:")
        print("   # 创建示例图片数据")
        print("   image_data = b'fake_image_data'")
        print("   media = wp.media.upload_from_bytes(")
        print("       file_data=image_data,")
        print("       filename='generated_image.jpg',")
        print("       mime_type='image/jpeg',")
        print("       title='生成的图片'")
        print("   )")
        
        # 3. 关联到文章
        print("\n3. 将媒体关联到文章:")
        print("   # 上传并关联到特定文章")
        print("   media = wp.media.upload(")
        print("       file_path='image.jpg',")
        print("       post=123,  # 文章ID")
        print("       title='文章配图'")
        print("   )")
        
        print("✓ 媒体上传功能演示完成！\n")
        
    except Exception as e:
        print(f"媒体上传演示失败: {e}\n")
    
    finally:
        wp.close()


def demo_custom_fields():
    """演示自定义字段管理"""
    print("=== 自定义字段管理演示 ===\n")
    
    wp = WordPress("https://coralera.org")
    
    try:
        # 1. 创建带自定义字段的文章
        print("1. 创建带自定义字段的文章:")
        
        custom_meta = {
            "featured": "yes",
            "reading_time": "5",
            "difficulty": "beginner",
            "tags_custom": ["python", "wordpress", "api"]
        }
        
        print("   post = wp.posts.create(")
        print("       title='带自定义字段的文章',")
        print("       content='<p>文章内容</p>',")
        print("       status=PostStatus.DRAFT,")
        print(f"       meta={custom_meta}")
        print("   )")
        
        # 2. 更新自定义字段
        print("\n2. 更新自定义字段:")
        
        updated_meta = {
            "featured": "no",
            "reading_time": "8",
            "last_updated": datetime.now().isoformat()
        }
        
        print("   updated_post = wp.posts.update(")
        print("       post_id=123,")
        print(f"       meta={updated_meta}")
        print("   )")
        
        # 3. 查询带自定义字段的文章
        print("\n3. 查询带自定义字段的文章:")
        print("   # 使用自定义查询参数")
        print("   query = create_query()")
        print("       .custom('meta_key', 'featured')")
        print("       .custom('meta_value', 'yes')")
        print("       .build()")
        print("   featured_posts = wp.posts.list(**query)")
        
        print("✓ 自定义字段管理演示完成！\n")
        
    except Exception as e:
        print(f"自定义字段演示失败: {e}\n")
    
    finally:
        wp.close()


def demo_comment_management():
    """演示评论管理"""
    print("=== 评论管理演示 ===\n")
    
    wp = WordPress("https://coralera.org")
    
    try:
        # 1. 获取评论列表
        print("1. 获取评论列表:")
        print("   # 获取最新的待审核评论")
        print("   pending_comments = wp.comments.list(")
        print("       status='hold',")
        print("       per_page=10,")
        print("       order='desc'")
        print("   )")
        
        # 2. 创建评论
        print("\n2. 创建评论:")
        print("   # 为文章添加评论")
        print("   comment = wp.comments.create(")
        print("       post=123,")
        print("       content='这是一条很好的文章！',")
        print("       author_name='访客',")
        print("       author_email='visitor@example.com',")
        print("       status='approve'")
        print("   )")
        
        # 3. 批量审核评论
        print("\n3. 批量审核评论:")
        print("   # 批准多条评论")
        print("   for comment_id in [1, 2, 3]:")
        print("       wp.comments.update(")
        print("           comment_id,")
        print("           status='approve'")
        print("       )")
        
        # 4. 回复评论
        print("\n4. 回复评论:")
        print("   # 回复特定评论")
        print("   reply = wp.comments.create(")
        print("       post=123,")
        print("       parent=456,  # 父评论ID")
        print("       content='感谢您的评论！',")
        print("       author_name='管理员'")
        print("   )")
        
        print("✓ 评论管理演示完成！\n")
        
    except Exception as e:
        print(f"评论管理演示失败: {e}\n")
    
    finally:
        wp.close()


def demo_best_practices():
    """演示最佳实践"""
    print("=== 最佳实践演示 ===\n")
    
    # 1. 使用上下文管理器
    print("1. 使用上下文管理器自动管理连接:")
    print("   with WordPress('https://coralera.org') as wp:")
    print("       posts = wp.posts.list()")
    print("   # 连接自动关闭")
    
    # 2. 异步操作最佳实践
    print("\n2. 异步操作最佳实践:")
    print("   async with AsyncWordPress('https://coralera.org') as wp:")
    print("       # 并发操作")
    print("       tasks = [wp.posts.get(i) for i in range(1, 6)]")
    print("       posts = await asyncio.gather(*tasks, return_exceptions=True)")
    
    # 3. 错误处理最佳实践
    print("\n3. 错误处理最佳实践:")
    print("   try:")
    print("       post = wp.posts.get(post_id)")
    print("   except NotFoundError:")
    print("       # 处理文章不存在")
    print("       pass")
    print("   except ValidationError as e:")
    print("       # 处理验证错误")
    print("       logger.error(f'验证失败: {e}')")
    print("   except WordPressError as e:")
    print("       # 处理其他WordPress错误")
    print("       logger.error(f'WordPress错误: {e}')")
    
    # 4. 分页处理最佳实践
    print("\n4. 分页处理最佳实践:")
    print("   def get_all_posts(wp):")
    print("       all_posts = []")
    print("       page = 1")
    print("       while True:")
    print("           posts = wp.posts.list(page=page, per_page=100)")
    print("           if not posts:")
    print("               break")
    print("           all_posts.extend(posts)")
    print("           page += 1")
    print("       return all_posts")
    
    # 5. 认证最佳实践
    print("\n5. 认证最佳实践:")
    print("   # 生产环境推荐使用应用程序密码")
    print("   wp = WordPress(")
    print("       'https://coralera.org',")
    print("       username=os.getenv('WP_USERNAME'),")
    print("       app_password=os.getenv('WP_APP_PASSWORD')")
    print("   )")
    
    print("✓ 最佳实践演示完成！\n")


def main():
    """主函数 - 运行所有演示"""
    print("WordPress REST API Python客户端 - 高级使用示例\n")
    print("注意：这些示例需要实际的WordPress站点才能完全运行")
    print("请根据需要修改WordPress站点URL和认证信息\n")
    
    # 运行各种演示
    demo_enum_string_compatibility()
    demo_advanced_queries()
    demo_error_handling()
    demo_media_upload()
    demo_custom_fields()
    demo_comment_management()
    demo_best_practices()
    
    # 异步演示
    print("运行异步操作演示...")
    try:
        asyncio.run(demo_async_batch_operations())
    except Exception as e:
        print(f"异步演示失败: {e}")
    
    print("=== 所有高级功能演示完成 ===")
    print("\n要运行实际的API操作，请:")
    print("1. 设置真实的WordPress站点URL")
    print("2. 配置正确的认证信息")
    print("3. 根据需要修改示例代码")


if __name__ == "__main__":
    main()