# 生产部署示例 Dockerfile（使用 Gunicorn + UvicornWorker）
# 构建镜像：
#   docker build -t wp-python-fastapi:prod -f examples/deploy/Dockerfile .
# 启动容器（需映射端口并挂载配置/静态资源等）：
#   docker run --rm -p 8000:8000 --env-file ./.env wp-python-fastapi:prod

FROM python:3.11-slim

ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 系统依赖（可按需精简）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN curl -sSL https://install.python-poetry.org | python -\
    && ln -sf ${POETRY_HOME}/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# 预先复制项目依赖声明，便于缓存
COPY pyproject.toml poetry.lock* ./

# 安装依赖（生产环境）
RUN poetry install --only main --no-interaction --no-ansi

# 复制项目源代码
COPY src ./src
COPY examples ./examples
COPY doc ./doc
COPY README.md ./README.md

# 默认使用 .env（实际部署请挂载 .env 文件或通过环境变量传入）
ENV LOG_LEVEL=INFO

# 暴露端口
EXPOSE 8000

# 入口：使用 FastAPI 插件生产模式（Gunicorn + UvicornWorker）
# 提供一个轻量启动脚本，方便覆盖
CMD ["bash", "-lc", "poetry run python examples/fastapi_plugin_example.py --start"]
