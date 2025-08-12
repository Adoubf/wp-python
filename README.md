# wp-python - WordPress REST API Python 客户端

一个现代、易用、带简体中文注释与示例的 WordPress REST API Python 客户端。

- 同步与异步客户端（WordPress / AsyncWordPress）
- 覆盖文章、页面、分类、标签、用户、媒体、评论等常用服务
- 查询构建器（create_query）与辅助工具
- 多种认证方式：应用程序密码、基础认证、JWT、Cookie+Nonce
- 可扩展插件系统与 FastAPI 插件
- 完整中文示例，快速上手

注意：在本项目中，所有运行与测试请使用 Poetry 虚拟环境。运行命令需要加前缀：
- 示例脚本：poetry run python examples/xxx.py
- 测试：poetry run python -m pytest tests/


## 安装与环境

1) 安装依赖（确保已安装 Poetry）

```
poetry install
```

2) 准备环境变量

- 推荐复制 `.env.dev` 为 `.env` 并根据你的站点修改：
  - WP_BASE_URL=https://your-wordpress-site.com
  - WP_USERNAME=your-username
  - WP_APP_PASSWORD=your-application-password  # 推荐
  - （可选）WP_PASSWORD=your-password          # 基础认证
  - （可选）WP_JWT_TOKEN=your-jwt-token       # JWT
  - LOG_LEVEL=INFO

3) 运行示例时务必带上 Poetry 前缀：

```
poetry run python examples/quick_start.py --dev
```


## 快速开始（Quick Start）

快速完成连接测试并执行常见操作：

```
poetry run python examples/quick_start.py --dev
```

该示例将演示：
- 从 .env/.env.dev 读取配置与日志初始化
- 测试连接与获取站点信息
- 文章/页面/分类/标签/用户/媒体/评论 常见读取接口
- 查询构建器 create_query 的基本用法
- 同步与异步两种调用方式


## 示例总览（examples/）

本仓库提供了覆盖全功能的中文示例，建议按序阅读与尝试：

- 快速上手：
  - examples/quick_start.py（强烈推荐先看）
- 环境与日志：
  - examples/env_config_example.py（如何加载 .env 并初始化日志器）
- 常用与高级用法：
  - examples/common_usage.py（文章/页面/分类/标签/用户/媒体/评论 的常用 CRUD 与查询）
  - examples/advanced_usage.py（复杂查询、异步批量、错误处理、文件上传、自定义字段）
- 认证方式：
  - examples/auth_methods.py（app password、basic、jwt、cookie+nonce 多种方案）
- 插件体系：
  - examples/plugin_system_example.py（不依赖 FastAPI 的插件生命周期演示）
  - examples/fastapi_plugin_example.py（集成 FastAPI 提供 REST 服务）
- 生产部署：
  - examples/deploy/Dockerfile（Gunicorn + UvicornWorker，健康检查 /api/v1/health）
- 媒体上传：
  - examples/media_upload_demo.py（附最小样例图片，支持 --cleanup 删除）
- 数据迁移：
  - examples/migrate_from_csv.py（从 CSV 批量创建文章并上传封面图）
  - examples/migrate_from_markdown.py（从 Markdown 目录批量创建文章并上传封面图）
- 进阶查询：
  - examples/query_cookbook.py（复杂筛选组合与性能/分页最佳实践）

所有示例运行请使用：

```
poetry run python examples/<示例文件>.py [参数]
```


## 基本用法

同步客户端：

```python
from wp_python import WordPress
from wp_python.utils import get_config

cfg = get_config()  # 自动读取 .env 或 .env.dev
with WordPress(
    cfg.base_url,
    **cfg.get_auth_config(),
    **cfg.get_client_config()
) as wp:
    posts = wp.posts.list(per_page=5)
    for p in posts:
        print(p.title.rendered if p.title else "无标题")
```

异步客户端：

```python
import asyncio
from wp_python import AsyncWordPress
from wp_python.utils import get_config

async def main():
    cfg = get_config()
    async with AsyncWordPress(
        cfg.base_url,
        **cfg.get_auth_config(),
        **cfg.get_client_config()
    ) as wp:
        posts = await wp.posts.list(per_page=5)
        print(len(posts))

asyncio.run(main())
```


## 查询构建器

```python
from wp_python.utils import create_query
from wp_python.core.models import PostStatus

query = (create_query()
         .per_page(10)
         .status([PostStatus.PUBLISH])
         .order_by("date", "desc")
         .build())

posts = wp.posts.list(**query)
```


## 认证方式

详见 examples/auth_methods.py，命令示例：

```
poetry run python examples/auth_methods.py --method app_password
poetry run python examples/auth_methods.py --method basic
poetry run python examples/auth_methods.py --method jwt
poetry run python examples/auth_methods.py --method cookie
```

推荐在生产环境使用“应用程序密码”方案。


## FastAPI 插件快速启动

```
poetry run python examples/fastapi_plugin_example.py --start
```

启动后可访问：
- http://localhost:8000/docs
- http://localhost:8000/redoc
- http://localhost:8000/api/v1/


## 测试

```
poetry run python -m pytest tests/
```


## 反馈与贡献

- 提交 Issue 或 Pull Request 前，请先运行示例与测试确保通过
- 欢迎完善文档与中文注释，帮助更多用户快速上手
