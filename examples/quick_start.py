#!/usr/bin/env python3
"""
WordPress REST API Python 客户端 - 快速上手示例

目标：帮助新用户在 5 分钟内完成环境配置、连接测试，并完成一次完整的内容操作流程。

包含内容：
- 使用 .env/.env.dev 环境配置（推荐）
- 初始化同步客户端和异步客户端
- 获取站点信息与连接测试
- 文章/页面/分类/标签/用户/媒体/评论 的常见操作调用示例
- 日志系统与错误处理

运行方式：
- 使用开发环境: poetry run python examples/quick_start.py --dev
- 使用生产环境: poetry run python examples/quick_start.py

注意：
- 实际读写操作（create/update/delete）需要正确的认证与权限；
- 示例中包含了“演示代码片段”的打印，帮助你替换为真实参数后运行。
"""

import asyncio
import sys

from wp_python import WordPress, AsyncWordPress
from wp_python.core.models import PostStatus
from wp_python.utils import create_query, setup_logging, get_config


def choose_env():
    """根据命令行参数选择使用 .env 或 .env.dev 配置文件。
    返回 get_config() 的实例。
    """
    use_dev = len(sys.argv) > 1 and sys.argv[1] == "--dev"
    env_file = ".env.dev" if use_dev else ".env"
    print(f"使用环境文件: {env_file}")
    return get_config(env_file)


def sync_flow(wp: WordPress):
    """同步完整流程示例：测试连接 -> 文章/页面/分类/标签/用户/媒体/评论 常见操作。
    注意：读写接口（create/update/delete）需要你的站点具备权限；
    若权限不足请先仅尝试 list/get。
    """
    logger = setup_logging(level="INFO")

    # 1. 测试连接与站点信息
    logger.progress("测试连接与获取站点信息...")
    info = wp.test_connection()
    logger.success(f"连接成功: {info['status']} -> {info['api_url']}")

    site_info = wp.get_site_info()
    logger.info(f"站点名称: {site_info.get('name')}")
    logger.info(f"站点描述: {site_info.get('description')}")

    # 2. 文章：列表 + 创建/更新/删除（演示）
    print("\n[文章] 获取最新发布的文章列表...")
    posts = wp.posts.list(per_page=3, status=[PostStatus.PUBLISH])
    for p in posts:
        print(f"- {p.title.rendered if p.title else '无标题'} (ID: {p.id})")

    print("\n[文章] 创建/更新/删除（示例代码，按需启用）:")
    print("""
# new_post = wp.posts.create(
#     title="QuickStart 创建的文章",
#     content="<p>内容...</p>",
#     status=PostStatus.DRAFT
# )
# updated = wp.posts.update(new_post.id, title="更新标题")
# wp.posts.delete(new_post.id, force=True)
""")

    # 3. 使用查询构建器筛选文章
    print("\n[文章] 使用查询构建器示例:")
    query = (create_query()
             .per_page(5)
             .status([PostStatus.PUBLISH])
             .order_by("date", "desc")
             .build())
    posts2 = wp.posts.list(**query)
    print(f"通过查询获取 {len(posts2)} 篇文章")

    # 4. 页面
    print("\n[页面] 列出页面:")
    pages = wp.pages.list(per_page=3)
    for pg in pages:
        print(f"- {pg.title.rendered if pg.title else '无标题'} (ID: {pg.id})")

    # 5. 分类/标签
    print("\n[分类] 列出分类:")
    cats = wp.categories.list(per_page=5)
    for c in cats:
        print(f"- {c.name} (ID: {c.id}, 文章数: {c.count})")

    print("\n[标签] 列出标签:")
    tags = wp.tags.list(per_page=5)
    for t in tags:
        print(f"- {t.name} (ID: {t.id}, 文章数: {t.count})")

    # 6. 用户（需要认证）
    print("\n[用户] 获取当前用户信息（需要认证）:")
    try:
        me = wp.users.get_me()
        print(f"- 当前用户: {me.name} ({me.email}) 角色: {me.roles}")
    except Exception as e:
        logger.warning(f"无法获取当前用户信息: {e}")

    # 7. 评论（只演示查询与示例代码片段）
    print("\n[评论] 获取最新评论:")
    comments = wp.comments.list(per_page=3, status='approve')
    for c in comments:
        print(f"- {c.author_name}: {c.content.rendered[:40]}...")

    print("\n[评论] 创建/审核（示例代码，按需启用）:")
    print("""
# comment = wp.comments.create(
#     post=123,  # 文章ID
#     content="这是一条很棒的文章！",
#     author_name="访客",
#     author_email="visitor@example.com",
#     status='approve'
# )
# wp.comments.update(comment.id, status='approve')
""")

    # 8. 媒体（仅演示接口形态）
    print("\n[媒体] 列出媒体:")
    media_list = wp.media.list(per_page=3)
    for m in media_list:
        print(f"- {m.title.rendered if m.title else '无标题'} ({m.mime_type}) -> {m.source_url}")

    print("\n[媒体] 上传文件（示例代码，按需启用）:")
    print("""
# media = wp.media.upload(
#     file_path='path/to/image.jpg',
#     title='上传的图片',
#     alt_text='ALT',
#     caption='说明'
# )
# media2 = wp.media.upload_from_bytes(
#     file_data=b'...bytes...',
#     filename='pic.jpg',
#     mime_type='image/jpeg',
#     title='通过字节上传'
# )
""")

    logger.success("快速上手流程完成！")


async def async_flow(config):
    """异步完整流程示例：与 sync_flow 类似，但展示 async/await 使用方式。"""
    logger = setup_logging(level="INFO")
    async with AsyncWordPress(
        config.base_url,
        **config.get_auth_config(),
        **config.get_client_config()
    ) as wp:
        logger.progress("(异步) 测试连接...")
        info = await wp.test_connection()
        logger.success(f"(异步) 连接成功: {info['api_url']}")

        # 并发获取文章/页面/分类
        posts_task = wp.posts.list(per_page=3)
        pages_task = wp.pages.list(per_page=3)
        cats_task = wp.categories.list(per_page=3)
        posts, pages, cats = await asyncio.gather(posts_task, pages_task, cats_task)
        print(f"(异步) 文章 {len(posts)} / 页面 {len(pages)} / 分类 {len(cats)}")

        # 异步创建文章（示例代码，按需启用）
        print("""
# new_post = await wp.posts.create(
#     title="异步创建的文章",
#     content="<p>内容</p>",
#     status=PostStatus.DRAFT
# )
# await wp.posts.update(new_post.id, title="异步更新标题")
# await wp.posts.delete(new_post.id, force=True)
""")

    logger.info("(异步) 示例结束")


def main():
    print("=== WordPress REST API Python 客户端 - 快速上手 ===\n")
    config = choose_env()

    # 使用同步客户端（推荐先从同步开始）
    with WordPress(
        config.base_url,
        **config.get_auth_config(),
        **config.get_client_config()
    ) as wp:
        sync_flow(wp)

    # 演示异步客户端
    print("\n开始演示异步客户端用法...")
    asyncio.run(async_flow(config))

    print("\n使用指引：")
    print("- 修改 .env 或 .env.dev 中的站点与认证信息")
    print("- 运行: poetry run python examples/quick_start.py [--dev]")


if __name__ == "__main__":
    main()
