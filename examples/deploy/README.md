# 从零部署 FastAPI 到生产（Dockerfile + Gunicorn + 健康检查）

本示例展示如何把本项目的 FastAPI 插件以生产模式部署（Gunicorn + UvicornWorker）。

包含：
- Dockerfile（examples/deploy/Dockerfile）
- 生产运行命令（Gunicorn + UvicornWorker）
- 健康检查端点（/api/v1/health）

## 准备配置

1) 拷贝 .env.dev 到 .env，并修改为你的生产配置：

```
WP_BASE_URL=https://your-wordpress-site.com
WP_USERNAME=your_user
WP_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
LOG_LEVEL=INFO
```

2) 构建镜像：

```
docker build -t wp-python-fastapi:prod -f examples/deploy/Dockerfile .
```

3) 运行容器：

```
docker run --rm -p 8000:8000 --env-file ./.env wp-python-fastapi:prod
```

4) 验证健康检查与文档：

- http://localhost:8000/api/v1/health
- http://localhost:8000/docs
- http://localhost:8000/redoc

## 自定义 Gunicorn 参数

如需调整并发、超时、日志等级等，可修改 FastAPI 插件初始化配置（examples/fastapi_plugin_example.py 中的 plugin_config），或编写自定义启动脚本：

```
#!/usr/bin/env bash
set -euo pipefail

# 示例：通过环境变量控制进程数与端口
: "${HOST:=0.0.0.0}"
: "${PORT:=8000}"
: "${WORKERS:=4}"

exec poetry run python examples/fastapi_plugin_example.py --start
```

也可以直接使用纯 Gunicorn 命令（若导出 app 对象）：

```
# 假设我们有一个 main:app 的 FastAPI 实例
# gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 main:app
```

## 生产注意事项

- 建议开启 HTTPS（前置 Nginx/Traefik）
- 合理配置 CORS origins
- 关闭或限制 docs/redoc/openapi（生产中可通过环境关闭）
- 日志使用 stdout/stderr，让容器平台收集
- 结合健康检查和自动重启策略（如 Docker/Swarm/K8s）
