#!/usr/bin/env python3
"""
完整迁移脚本示例：从 CSV 批量创建文章并上传封面图

- CSV 格式（示例见 examples/sample_data/posts.csv）：
  title,content,status,category_ids,tag_ids,cover_image
  第一篇文章标题,<p>HTML 内容</p>,draft,"1|2","3|4",examples/sample_data/sample_image.jpg

- 行为：
  - 读取 CSV，每行生成一篇文章
  - 若提供 cover_image（本地路径），则先上传媒体并关联到文章（featured_media）
  - 支持用 | 分隔的分类和标签 ID 列

运行：
poetry run python examples/migrate_from_csv.py --csv examples/sample_data/posts.csv
"""

import csv
from pathlib import Path
import argparse

from wp_python import WordPress
from wp_python.core.models import PostStatus
from wp_python.utils import get_config, setup_logging


def parse_ids(cell: str) -> list[int]:
    if not cell:
        return []
    return [int(x) for x in str(cell).split("|") if str(x).strip().isdigit()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="CSV 文件路径")
    args = parser.parse_args()

    logger = setup_logging(level="INFO")
    cfg = get_config()
    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 文件不存在: {csv_path}")

    created = 0
    with WordPress(cfg.base_url, **cfg.get_auth_config(), **cfg.get_client_config()) as wp:
        with csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("title", "").strip()
                content = row.get("content", "").strip()
                status = row.get("status", "draft").strip()
                category_ids = parse_ids(row.get("category_ids", ""))
                tag_ids = parse_ids(row.get("tag_ids", ""))
                cover_image = row.get("cover_image", "").strip()

                # 可选：上传封面图
                featured_media_id = None
                if cover_image:
                    p = Path(cover_image)
                    if p.exists():
                        logger.info(f"上传封面图: {p}")
                        media = wp.media.upload(file_path=str(p), title=f"封面-{title}")
                        featured_media_id = media.id
                    else:
                        logger.warning(f"封面图不存在，跳过: {p}")

                logger.info(f"创建文章: {title}")
                post = wp.posts.create(
                    title=title,
                    content=content,
                    status=status if status else PostStatus.DRAFT,
                    categories=category_ids or None,
                    tags=tag_ids or None,
                    featured_media=featured_media_id,
                )
                created += 1
                logger.success(f"创建成功: ID={post.id}")

    logger.success(f"迁移完成，共创建 {created} 篇文章")
    print("\n运行示例：")
    print("poetry run python examples/migrate_from_csv.py --csv examples/sample_data/posts.csv")


if __name__ == "__main__":
    main()
