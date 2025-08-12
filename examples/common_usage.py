#!/usr/bin/env python3
"""
WordPress REST API Python客户端常用功能示例

演示日常开发中最常用的功能，包括：
- 文章的增删改查
- 页面管理
- 分类和标签操作
- 用户管理
- 媒体文件处理
- 评论管理
"""

from datetime import datetime
from wp_python import WordPress
from wp_python.core.models import PostStatus, PostFormat
from wp_python.utils import create_query
from wp_python.utils import get_config


def setup_client():
    """设置WordPress客户端"""
    config = get_config()

    # 请替换为您的实际WordPress站点信息
    return WordPress(
        config.base_url,
        # 推荐使用应用程序密码
        username=config.username,
        app_password=config.app_password

        # 或使用基础认证（仅用于开发）
        # username='your-username',
        # password='your-password'
    )


def demo_post_operations():
    """演示文章操作"""
    print("=== 文章操作演示 ===\n")
    
    with setup_client() as wp:
        try:
            # 1. 获取文章列表
            print("1. 获取最新发布的文章:")
            posts = wp.posts.list(
                per_page=5,
                status=['publish'],  # 支持字符串
                order='desc',
                orderby='date'
            )
            
            for post in posts:
                print(f"   - {post.title.rendered} (ID: {post.id})")
            
            # 2. 使用枚举获取文章
            print("\n2. 使用枚举获取草稿文章:")
            drafts = wp.posts.list(
                per_page=3,
                status=[PostStatus.DRAFT],  # 使用枚举
                order='desc'
            )
            
            for draft in drafts:
                print(f"   - {draft.title.rendered} (草稿)")
            
            # 3. 创建新文章
            print("\n3. 创建新文章:")
            new_post = wp.posts.create(
                title="Python API 创建的文章",
                content="<p>这是通过Python WordPress API创建的文章。</p><p>支持HTML内容。</p>",
                excerpt="文章摘要",
                status=PostStatus.DRAFT,  # 创建为草稿
                format=PostFormat.STANDARD,
                categories=[1],  # 分类ID
                tags=[1, 2],     # 标签ID
                meta={           # 自定义字段
                    "custom_field": "自定义值",
                    "author_note": "这是作者备注"
                }
            )
            print(f"   ✓ 创建成功: {new_post.title.rendered} (ID: {new_post.id})")
            
            # 4. 更新文章
            print("\n4. 更新文章:")
            updated_post = wp.posts.update(
                new_post.id,
                title="更新后的文章标题",
                content="<p>这是更新后的文章内容。</p>",
                status=PostStatus.PUBLISH  # 发布文章
            )
            print(f"   ✓ 更新成功: {updated_post.title.rendered}")
            
            # 5. 获取单个文章
            print("\n5. 获取单个文章详情:")
            post_detail = wp.posts.get(new_post.id)
            print(f"   标题: {post_detail.title.rendered}")
            print(f"   状态: {post_detail.status}")
            print(f"   发布时间: {post_detail.date}")
            
            # 6. 删除文章
            print("\n6. 删除文章:")
            wp.posts.delete(new_post.id, force=True)  # 强制删除
            print("   ✓ 文章已删除")
            
        except Exception as e:
            print(f"文章操作失败: {e}")


def demo_page_operations():
    """演示页面操作"""
    print("\n=== 页面操作演示 ===\n")
    
    with setup_client() as wp:
        try:
            # 1. 获取页面列表
            print("1. 获取页面列表:")
            pages = wp.pages.list(per_page=5)
            
            for page in pages:
                print(f"   - {page.title.rendered} (ID: {page.id}, 父页面: {page.parent})")
            
            # 2. 创建新页面
            print("\n2. 创建新页面:")
            new_page = wp.pages.create(
                title="API创建的页面",
                content="<h1>页面标题</h1><p>这是页面内容。</p>",
                status=PostStatus.PUBLISH,
                parent=0,  # 顶级页面
                menu_order=1  # 菜单排序
                # template="page-custom.php"  # 移除模板参数，避免无效参数错误
            )
            print(f"   ✓ 创建成功: {new_page.title.rendered} (ID: {new_page.id})")
            
            # 3. 创建子页面
            print("\n3. 创建子页面:")
            child_page = wp.pages.create(
                title="子页面",
                content="<p>这是子页面内容。</p>",
                status=PostStatus.PUBLISH,
                parent=new_page.id,  # 设置父页面
                menu_order=1
            )
            print(f"   ✓ 子页面创建成功: {child_page.title.rendered}")
            
            # 4. 更新页面
            print("\n4. 更新页面:")
            wp.pages.update(
                new_page.id,
                title="更新后的页面标题",
                content="<h1>更新后的页面</h1><p>内容已更新。</p>"
            )
            print("   ✓ 页面更新成功")
            
        except Exception as e:
            print(f"页面操作失败: {e}")


def demo_category_tag_operations():
    """演示分类和标签操作"""
    print("\n=== 分类和标签操作演示 ===\n")
    
    with setup_client() as wp:
        try:
            # 1. 获取分类列表
            print("1. 获取分类列表:")
            categories = wp.categories.list(per_page=10)
            
            for category in categories:
                print(f"   - {category.name} (ID: {category.id}, 文章数: {category.count})")
            
            # 2. 创建新分类
            print("\n2. 创建新分类:")
            try:
                new_category = wp.categories.create(
                    name=f"Python开发-{datetime.now().strftime('%H%M%S')}",  # 添加时间戳避免重复
                    description="Python相关的开发文章",
                    slug=f"python-dev-{datetime.now().strftime('%H%M%S')}",
                    parent=0  # 顶级分类
                )
                print(f"   ✓ 分类创建成功: {new_category.name} (ID: {new_category.id})")
            except Exception as e:
                print(f"   ✗ 分类创建失败（可能已存在）: {e}")
            
            # 3. 创建子分类
            print("\n3. 创建子分类:")
            sub_category = wp.categories.create(
                name="Django框架",
                description="Django相关文章",
                slug="django",
                parent=new_category.id  # 设置父分类
            )
            print(f"   ✓ 子分类创建成功: {sub_category.name}")
            
            # 4. 获取标签列表
            print("\n4. 获取标签列表:")
            tags = wp.tags.list(per_page=10)
            
            for tag in tags:
                print(f"   - {tag.name} (ID: {tag.id}, 文章数: {tag.count})")
            
            # 5. 创建新标签
            print("\n5. 创建新标签:")
            new_tag = wp.tags.create(
                name="API开发",
                description="API开发相关",
                slug="api-development"
            )
            print(f"   ✓ 标签创建成功: {new_tag.name} (ID: {new_tag.id})")
            
            # 6. 批量创建标签
            print("\n6. 批量创建标签:")
            tag_names = ["REST API", "Python", "WordPress", "自动化"]
            
            for tag_name in tag_names:
                try:
                    tag = wp.tags.create(
                        name=tag_name,
                        slug=tag_name.lower().replace(" ", "-")
                    )
                    print(f"   ✓ 创建标签: {tag.name}")
                except Exception as e:
                    print(f"   ✗ 创建标签失败 {tag_name}: {e}")
            
        except Exception as e:
            print(f"分类标签操作失败: {e}")


def demo_user_operations():
    """演示用户操作"""
    print("\n=== 用户操作演示 ===\n")
    
    with setup_client() as wp:
        try:
            # 1. 获取用户列表
            print("1. 获取用户列表:")
            users = wp.users.list(per_page=5)
            
            for user in users:
                print(f"   - {user.name} ({user.username}) - 角色: {user.roles}")
            
            # 2. 获取当前用户信息
            print("\n2. 获取当前用户信息:")
            current_user = wp.users.get_me()
            print(f"   当前用户: {current_user.name} ({current_user.email})")
            print(f"   角色: {current_user.roles}")
            
            # 3. 创建新用户（需要管理员权限）
            print("\n3. 创建新用户:")
            try:
                timestamp = datetime.now().strftime('%H%M%S')
                new_user = wp.users.create(
                    username=f"api_user_{timestamp}",  # 添加时间戳避免重复
                    email=f"apiuser_{timestamp}@example.com",
                    password="secure_password_123",
                    name="API用户",
                    first_name="API",
                    last_name="用户",
                    roles=["author"],  # 设置为作者角色
                    description="通过API创建的用户"
                )
                print(f"   ✓ 用户创建成功: {new_user.name} (ID: {new_user.id})")
            except Exception as e:
                print(f"   ✗ 用户创建失败（可能权限不足或已存在）: {e}")
            
            # 4. 更新用户信息
            print("\n4. 更新当前用户信息:")
            try:
                updated_user = wp.users.update_me(
                    description="更新后的用户描述",
                    url="https://example.com"
                )
                print(f"   ✓ 用户信息更新成功: {updated_user.name}")
            except Exception as e:
                print(f"   ✗ 用户更新失败: {e}")
            
        except Exception as e:
            print(f"用户操作失败: {e}")


def demo_media_operations():
    """演示媒体操作"""
    print("\n=== 媒体操作演示 ===\n")
    
    with setup_client() as wp:
        try:
            # 1. 获取媒体列表
            print("1. 获取媒体列表:")
            media_list = wp.media.list(per_page=5)
            
            for media in media_list:
                print(f"   - {media.title.rendered} ({media.mime_type})")
                print(f"     URL: {media.source_url}")
            
            # 2. 模拟文件上传（实际使用时需要真实文件）
            print("\n2. 文件上传示例:")
            print("   # 从文件路径上传")
            print("   media = wp.media.upload(")
            print("       file_path='path/to/image.jpg',")
            print("       title='上传的图片',")
            print("       alt_text='图片描述',")
            print("       caption='图片说明'")
            print("   )")
            
            print("\n   # 从字节数据上传")
            print("   with open('image.jpg', 'rb') as f:")
            print("       media = wp.media.upload_from_bytes(")
            print("           file_data=f.read(),")
            print("           filename='image.jpg',")
            print("           title='字节上传的图片'")
            print("       )")
            
            # 3. 更新媒体信息
            if media_list:
                print(f"\n3. 更新媒体信息 (ID: {media_list[0].id}):")
                try:
                    updated_media = wp.media.update(
                        media_list[0].id,
                        title="更新后的媒体标题",
                        alt_text="更新后的替代文本",
                        caption="更新后的说明"
                    )
                    print(f"   ✓ 媒体更新成功: {updated_media.title.rendered}")
                except Exception as e:
                    print(f"   ✗ 媒体更新失败: {e}")
            
        except Exception as e:
            print(f"媒体操作失败: {e}")


def demo_comment_operations():
    """演示评论操作"""
    print("\n=== 评论操作演示 ===\n")
    
    with setup_client() as wp:
        try:
            # 1. 获取评论列表
            print("1. 获取最新评论:")
            comments = wp.comments.list(per_page=5, status='approve')
            
            for comment in comments:
                print(f"   - {comment.author_name}: {comment.content.rendered[:50]}...")
            
            # 2. 获取待审核评论
            print("\n2. 获取待审核评论:")
            pending_comments = wp.comments.list(status='hold', per_page=3)
            
            for comment in pending_comments:
                print(f"   - 待审核: {comment.author_name} - {comment.content.rendered[:30]}...")
            
            # 3. 创建评论（需要文章ID）
            print("\n3. 创建评论示例:")
            print("   comment = wp.comments.create(")
            print("       post=123,  # 文章ID")
            print("       content='这是一条很棒的文章！',")
            print("       author_name='访客',")
            print("       author_email='visitor@example.com',")
            print("       status='approve'")
            print("   )")
            
            # 4. 批量审核评论
            print("\n4. 批量审核评论:")
            if pending_comments:
                for comment in pending_comments[:2]:  # 只处理前2条
                    try:
                        wp.comments.update(
                            comment.id,
                            status='approve'  # 批准评论
                        )
                        print(f"   ✓ 评论已批准: {comment.id}")
                    except Exception as e:
                        print(f"   ✗ 评论审核失败: {e}")
            
        except Exception as e:
            print(f"评论操作失败: {e}")


def demo_advanced_queries():
    """演示高级查询"""
    print("\n=== 高级查询演示 ===\n")
    
    with setup_client() as wp:
        try:
            # 1. 复杂文章查询
            print("1. 复杂文章查询:")
            
            # 查询最近7天的技术文章
            seven_days_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            query = (create_query()
                    .per_page(10)
                    .status([PostStatus.PUBLISH])
                    .categories([1, 2])  # 技术相关分类
                    .after(seven_days_ago)
                    .order_by("date", "desc")
                    .build())
            
            recent_posts = wp.posts.list(**query)
            print(f"   找到 {len(recent_posts)} 篇最近的技术文章")
            
            # 2. 搜索查询
            print("\n2. 搜索查询:")
            search_query = (create_query()
                           .search("Python WordPress")
                           .per_page(5)
                           .status(['publish'])
                           .build())
            
            search_results = wp.posts.list(**search_query)
            print(f"   搜索到 {len(search_results)} 篇相关文章")
            
            # 3. 分页查询
            print("\n3. 分页查询所有文章:")
            all_posts = []
            page = 1
            
            while True:
                try:
                    posts = wp.posts.list(
                        page=page,
                        per_page=10,
                        status=['publish']
                    )
                    
                    if not posts:
                        break
                    
                    all_posts.extend(posts)
                    print(f"   获取第 {page} 页: {len(posts)} 篇文章")
                    page += 1
                    
                    # 限制演示只获取前3页
                    if page > 3:
                        break
                        
                except Exception as e:
                    if "invalid_page_number" in str(e):
                        print(f"   已到达最后一页，停止分页查询")
                        break
                    else:
                        raise e
            
            print(f"   总共获取: {len(all_posts)} 篇文章")
            
        except Exception as e:
            print(f"高级查询失败: {e}")


def main():
    """主函数"""
    print("WordPress REST API Python客户端 - 常用功能演示\n")
    print("注意：请在运行前配置正确的WordPress站点信息和认证\n")
    
    try:
        # 运行各种演示
        demo_post_operations()
        demo_page_operations()
        demo_category_tag_operations()
        demo_user_operations()
        demo_media_operations()
        demo_comment_operations()
        demo_advanced_queries()
        
        print("\n=== 所有常用功能演示完成 ===")
        print("\n提示：")
        print("1. 修改 setup_client() 函数中的WordPress站点信息")
        print("2. 使用应用程序密码进行认证（推荐）")
        print("3. 根据实际需求调整示例代码")
        print("4. 查看 examples/advanced_usage.py 了解更多高级功能")
        
    except Exception as e:
        print(f"演示运行失败: {e}")
        print("请检查WordPress站点配置和网络连接")


if __name__ == "__main__":
    main()