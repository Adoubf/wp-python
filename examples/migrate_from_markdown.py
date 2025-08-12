#!/usr/bin/env python3
"""
完整迁移脚本示例：从 Markdown 目录批量创建文章并上传封面图

- Markdown 目录结构：
  examples/sample_data/md/
    post-1.md
    post-2.md
    assets/
      post-1.jpg
      post-2.jpg

- Markdown 元信息（YAML front matter，可选）：
  ---
  title: 标题
  status: draft
  categories: [1, 2]
  tags: [3, 4]
  cover_image: assets/post-1.jpg
  ---

运行：
poetry run python examples/migrate_from_markdown.py --dir examples/sample_data/md
"""

import argparse
from pathlib import Path
from typing import Any, Dict, List

from wp_python import WordPress
from wp_python.utils import get_config, setup_logging


def parse_front_matter(text: str) -> tuple[Dict[str, Any], str]:
    """解析简单 YAML front matter（仅示例，非完整 YAML 解析）。"""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    header = text[4:end]
    body = text[end + 5 :]

    meta: Dict[str, Any] = {}
    for line in header.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            # 粗略解析 [1, 2]
            items = [x.strip().strip(",") for x in v[1:-1].split(" ") if x.strip(", ")]
            try:
                meta[k] = [int(x) if x.isdigit() else x for x in items]
            except Exception:
                meta[k] = items
        else:
            meta[k] = v
    return meta, body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Markdown 根目录")
    args = parser.parse_args()

    logger = setup_logging(level="INFO")
    root = Path(args.dir)
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Markdown 目录不存在: {root}")

    cfg = get_config()
    created = 0

    with WordPress(cfg.base_url, **cfg.get_auth_config(), **cfg.get_client_config()) as wp:
        for md in sorted(root.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            meta, body = parse_front_matter(text)

            title = meta.get("title") or md.stem
            status = meta.get("status") or "draft"
            categories = meta.get("categories")
            tags = meta.get("tags")
            cover_image = meta.get("cover_image")

            # 可选：上传封面
            featured_media_id = None
            if cover_image:
                image_path = (root / cover_image).resolve()
                if image_path.exists():
                    logger.info(f"上传封面: {image_path}")
                    media = wp.media.upload(file_path=str(image_path), title=f"封面-{title}")
                    featured_media_id = media.id
                else:
                    logger.warning(f"封面不存在，跳过: {image_path}")

            logger.info(f"创建文章: {title}")
            post = wp.posts.create(
                title=title,
                content=body,
                status=status,
                categories=categories,
                tags=tags,
                featured_media=featured_media_id,
            )
            created += 1
            logger.success(f"创建成功: ID={post.id}")

    logger.success(f"Markdown 迁移完成，共创建 {created} 篇文章")
    print("\n运行示例：")
    print("poetry run python examples/migrate_from_markdown.py --dir examples/sample_data/md")


if __name__ == "__main__":
    main()
