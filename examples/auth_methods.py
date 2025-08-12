#!/usr/bin/env python3
"""
WordPress REST API Python 客户端 - 认证方式示例

目标：演示 wp-python 支持的多种认证方案，并给出实操指引。

支持的认证方式：
- 应用程序密码（推荐，WordPress 原生支持）
- 基础认证（Basic Auth，仅建议在开发环境或 HTTPS 且受信网络中使用）
- JWT 令牌（需要安装 JWT Authentication 插件）
- Cookie + Nonce（前端集成常用方案，需要在 WordPress 侧生成 nonce）

运行方式：
- poetry run python examples/auth_methods.py --method app_password
- poetry run python examples/auth_methods.py --method basic
- poetry run python examples/auth_methods.py --method jwt
- poetry run python examples/auth_methods.py --method cookie

准备工作：
- 将站点与认证信息写入 .env 或 .env.dev（参考 .env.dev 示例变量名）
- 或者替换下面示例中的占位参数
"""

import sys
from typing import Dict

from wp_python import WordPress
from wp_python.utils import get_config, setup_logging


def build_with_app_password():
    """应用程序密码认证（推荐）。
    需要：WP 后台 用户 -> 配置 应用程序密码，记录生成的 24 位密码。
    """
    cfg = get_config()
    return WordPress(
        cfg.base_url,
        username=cfg.username,
        app_password=cfg.app_password,
        **cfg.get_client_config()
    )


def build_with_basic_auth():
    """基础认证（开发期/受限环境）。
    注意：不建议在生产中长期使用；至少确保全站 HTTPS。
    """
    cfg = get_config()
    return WordPress(
        cfg.base_url,
        username=cfg.username,
        password=cfg.password,  # 来自 .env 或 .env.dev 的 WP_PASSWORD
        **cfg.get_client_config()
    )


def build_with_jwt():
    """JWT 令牌认证。
    需要：安装常见的 JWT Authentication for WP 插件，按插件说明配置。
    获取到 jwt token 后，直接传入 jwt_token 即可。
    """
    cfg = get_config()
    return WordPress(
        cfg.base_url,
        jwt_token=cfg.jwt_token,  # 来自 .env 或 .env.dev 的 WP_JWT_TOKEN
        **cfg.get_client_config()
    )


def build_with_cookie_nonce():
    """Cookie + Nonce 认证。
    适合与前端集成：前端从 WP 侧拿到 cookie 与 nonce，后端转发时带上。
    需要：X-WP-Nonce 值 和 对应的 cookies（例如 logged_in_*）。
    """
    cfg = get_config()

    # 示例占位：请替换为真实的 nonce 与 cookies
    cookies: Dict[str, str] = {
        # "wordpress_logged_in_xxx": "...",
        # "wp-settings-1": "...",
    }
    wp_nonce = None  # 如 "abcdef123456..." 来自 WP 端生成

    return WordPress(
        cfg.base_url,
        wp_nonce=wp_nonce,
        cookies=cookies,
        **cfg.get_client_config()
    )


def smoke_test(wp: WordPress):
    """连接冒烟测试：验证认证是否可用，读取一些公开数据。"""
    logger = setup_logging(level="INFO")
    info = wp.test_connection()
    logger.success(f"连接成功: {info['api_url']}")

    try:
        # 如果认证有效，以下调用也应成功（依据站点权限）
        me = wp.users.get_me()
        logger.info(f"当前用户: {me.name} / 角色: {me.roles}")
    except Exception as e:
        logger.warning(f"读取当前用户信息失败（可能未登录或权限不足）: {e}")

    # 不需要认证的公开数据
    posts = wp.posts.list(per_page=3)
    logger.info(f"读取公开文章成功: {len(posts)} 条")


def main():
    logger = setup_logging(level="INFO")
    method = None
    if len(sys.argv) > 2 and sys.argv[1] == "--method":
        method = sys.argv[2]
    else:
        print("未指定 --method，默认使用 app_password")
        method = "app_password"

    builders = {
        "app_password": build_with_app_password,
        "basic": build_with_basic_auth,
        "jwt": build_with_jwt,
        "cookie": build_with_cookie_nonce,
    }
    if method not in builders:
        print(f"不支持的认证方式: {method}")
        print("可选值：app_password | basic | jwt | cookie")
        sys.exit(1)

    cfg = get_config()  # 触发 .env/.env.dev 加载
    logger.info(f"站点: {cfg.base_url}")

    with builders[method]() as wp:
        smoke_test(wp)

    print("\n运行示例：")
    print("poetry run python examples/auth_methods.py --method app_password")
    print("poetry run python examples/auth_methods.py --method basic")
    print("poetry run python examples/auth_methods.py --method jwt")
    print("poetry run python examples/auth_methods.py --method cookie")


if __name__ == "__main__":
    main()
