#!/usr/bin/env python3
"""
媒体上传真实文件示例（可运行）

- 演示从本地小体积样例文件上传媒体，并在结束后可清理（删除）
- 样例文件：examples/sample_data/sample_image.jpg（占位：极小体积）
- 需要具备媒体上传权限（应用程序密码推荐）

运行：
poetry run python examples/media_upload_demo.py [--cleanup]

--cleanup: 成功上传后，演示删除该媒体，保持站点干净
"""

import argparse
from pathlib import Path

from wp_python import WordPress
from wp_python.utils import get_config, setup_logging

SAMPLE_DIR = Path(__file__).parent / "sample_data"
SAMPLE_FILE = SAMPLE_DIR / "sample_image.jpg"


def ensure_sample_file():
    """确保存在一个极小的 JPEG 样例文件。若不存在则生成一个最小化 JPEG。"""
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    if not SAMPLE_FILE.exists():
        # 写入一个最小 JPEG 头部 + 结束，适用于示例占位（某些 WP 可能拒绝极端简化图片，如失败请自备小图）
        SAMPLE_FILE.write_bytes(
            bytes.fromhex(
                "FFD8FFE000104A46494600010101006000600000FFDB004300280C0E0F0E0C28"
                "0E0F0F120F0F121717141214171C1B1C1C1C1C1C1C1C1C1C1C1CFFDA000C0301"
                "0002110311003F00D2CF20FFD9"
            )
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cleanup", action="store_true", help="上传成功后删除媒体")
    args = parser.parse_args()

    logger = setup_logging(level="INFO")
    ensure_sample_file()
    cfg = get_config()

    with WordPress(cfg.base_url, **cfg.get_auth_config(), **cfg.get_client_config()) as wp:
        logger.info(f"开始上传样例图片: {SAMPLE_FILE}")
        media = wp.media.upload(
            file_path=str(SAMPLE_FILE),
            title="示例-小图上传",
            alt_text="示例小图",
            caption="由 media_upload_demo.py 上传",
        )
        logger.success(f"上传成功: ID={media.id}, URL={media.source_url}")

        if args.cleanup:
            try:
                logger.info("按 --cleanup 请求，删除刚上传的媒体...")
                wp.media.delete(media.id, force=True)
                logger.success("媒体删除完成")
            except Exception as e:
                logger.warning(f"删除失败: {e}")

    print("\n运行指引：")
    print("poetry run python examples/media_upload_demo.py")
    print("poetry run python examples/media_upload_demo.py --cleanup")


if __name__ == "__main__":
    main()
