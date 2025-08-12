#!/usr/bin/env python3
"""
进阶查询 cookbook（复杂筛选组合与性能/分页最佳实践）

内容包含：
- 分类/标签/作者/日期范围等组合过滤
- 置顶、格式、关键字搜索、相关性排序
- 大量数据的分页遍历策略（带中断与错误处理）
- 限流与退避的简要示例（伪代码）

运行：
poetry run python examples/query_cookbook.py
"""

from datetime import datetime, timedelta
from typing import List

from wp_python import WordPress
from wp_python.core.models import PostStatus, PostFormat
from wp_python.utils import create_query, get_config, setup_logging


def print_posts(posts) -> None:
    for p in posts:
        title = p.title.rendered if getattr(p, "title", None) else "无标题"
        print(f"- {title} (ID: {p.id}, 状态: {p.status}, 日期: {p.date})")


def combo_filters(wp: WordPress):
    print("\n[组合过滤] 最近30天、分类[1,2]、排除标签[99]、作者[1]、按修改时间排序：")
    since = datetime.now() - timedelta(days=30)

    q = (
        create_query()
        .per_page(10)
        .status([PostStatus.PUBLISH])
        .categories([1, 2])
        .tags_exclude([99])
        .author([1])
        .after(since)
        .order_by("modified", "desc")
        .build()
    )
    posts = wp.posts.list(**q)
    print_posts(posts)


def sticky_and_format(wp: WordPress):
    print("\n[置顶与格式] 仅置顶，格式为标准/视频：")
    q = (
        create_query()
        .per_page(5)
        .status([PostStatus.PUBLISH])
        .sticky(True)
        .format([PostFormat.STANDARD, PostFormat.VIDEO])
        .order_by("date", "desc")
        .build()
    )
    posts = wp.posts.list(**q)
    print_posts(posts)


def search_relevance(wp: WordPress):
    print("\n[关键字搜索] 关键词：Python WordPress，按相关性排序：")
    q = (
        create_query()
        .search("Python WordPress")
        .per_page(10)
        .status([PostStatus.PUBLISH])
        .order_by("relevance", "desc")
        .build()
    )
    posts = wp.posts.list(**q)
    print_posts(posts)


def paginate_all(wp: WordPress, page_size: int = 50, max_pages: int = 10):
    print(f"\n[分页遍历] 每页 {page_size} 条，最多 {max_pages} 页：")

    all_posts: List = []
    page = 1
    while page <= max_pages:
        try:
            batch = wp.posts.list(page=page, per_page=page_size, status=[PostStatus.PUBLISH])
            if not batch:
                print("  已到达最后一页，提前结束")
                break
            print(f"  第 {page} 页：{len(batch)} 条")
            all_posts.extend(batch)
            page += 1
        except Exception as e:
            msg = str(e)
            if "invalid_page_number" in msg:
                print("  已到达最后一页，停止")
                break
            print(f"  请求失败：{e}，稍后重试（示例不实现重试，仅提示）")
            break
    print(f"合计 {len(all_posts)} 条")


def rate_limit_and_backoff_note():
    print("\n[限流与退避策略]（伪代码提示）：")
    print("""
# 伪代码示例：遇到 429 或连接错误时指数退避
# for attempt in range(0, MAX_RETRY):
#     try:
#         posts = wp.posts.list(per_page=100)
#         break
#     except RateLimitError:
#         sleep = min(BASE * (2 ** attempt), MAX_BACKOFF)
#         time.sleep(sleep)
#     except (TimeoutError, ConnectionError):
#         time.sleep(2)
# else:
#     raise RuntimeError("重试仍失败")
""")


def main():
    logger = setup_logging(level="INFO")
    cfg = get_config()
    with WordPress(cfg.base_url, **cfg.get_auth_config(), **cfg.get_client_config()) as wp:
        combo_filters(wp)
        sticky_and_format(wp)
        search_relevance(wp)
        paginate_all(wp, page_size=50, max_pages=5)
    rate_limit_and_backoff_note()

    print("\n运行：poetry run python examples/query_cookbook.py")


if __name__ == "__main__":
    main()
