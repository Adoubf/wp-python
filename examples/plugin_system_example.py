#!/usr/bin/env python3
"""
WordPress REST API Python 客户端 - 插件系统独立使用示例

目标：演示如何不启动 FastAPI，也能使用插件系统扩展功能。

包含内容：
- 插件基类 BasePlugin 与插件管理器 PluginManager 的用法
- 编写一个简单的插件：记录生命周期调用（initialize/start/stop）并输出信息
- 与 WordPress 客户端配合：在调用前后打印插件信息（示例）

运行方式：
- poetry run python examples/plugin_system_example.py
"""

from __future__ import annotations

from wp_python.plugin import BasePlugin, get_plugin_manager
from wp_python.utils import setup_logging, get_config
from wp_python import WordPress


class DemoLifecyclePlugin(BasePlugin):
    """演示插件生命周期的简单插件。"""

    def __init__(self) -> None:
        super().__init__(name="demo_lifecycle", version="1.0.0")
        self.started = False

    def initialize(self, config: dict | None = None) -> None:
        self.logger.info("DemoLifecyclePlugin 初始化完成")
        if config:
            self.configure(config)

    def start(self) -> None:
        self.started = True
        self.logger.success("DemoLifecyclePlugin 已启动")

    def stop(self) -> None:
        self.started = False
        self.logger.info("DemoLifecyclePlugin 已停止")

    def get_info(self) -> dict:
        info = super().get_info()
        info.update({"started": self.started})
        return info


def main():
    logger = setup_logging(level="INFO")

    # 1) 注册并启用自定义插件
    pm = get_plugin_manager()
    demo = DemoLifecyclePlugin()
    pm.register(demo)
    demo.initialize({"demo": True})
    demo.enable()
    demo.start()

    # 2) 创建 WordPress 客户端并执行一次简单调用
    cfg = get_config()
    with WordPress(
        cfg.base_url, **cfg.get_auth_config(), **cfg.get_client_config()
    ) as wp:
        logger.info("开始拉取文章列表（per_page=2）...")
        posts = wp.posts.list(per_page=2)
        logger.info(f"拉取完成，共 {len(posts)} 篇")

        print("\n插件信息:")
        print(demo.get_info())

    # 3) 停止与禁用插件
    demo.stop()
    demo.disable()

    logger.success("插件系统独立使用示例完成！")


if __name__ == "__main__":
    main()
