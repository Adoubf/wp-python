#!/usr/bin/env python3
"""
WordPress REST API FastAPI插件使用示例

演示如何使用FastAPI插件快速构建WordPress API服务。
"""

from wp_python.plugin import get_plugin_manager, FastAPIPlugin
from wp_python.utils import get_config, setup_logging


def demo_basic_usage():
    """基础使用演示"""
    print("=== FastAPI插件基础使用演示 ===\n")
    
    # 设置日志
    logger = setup_logging(level="INFO")
    
    # 获取插件管理器
    plugin_manager = get_plugin_manager()
    
    # 创建FastAPI插件
    fastapi_plugin = FastAPIPlugin()
    
    # 注册插件
    plugin_manager.register(fastapi_plugin)
    
    # 获取WordPress配置
    config = get_config('.env.dev')  # 使用开发环境配置
    
    # 配置插件
    plugin_config = {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": config.debug,
        "reload": True,
        "title": "WordPress REST API 服务",
        "description": "基于wp-python的WordPress REST API FastAPI服务",
        "version": "1.0.0",
        "cors_origins": ["*"],
        "wordpress_config": config.to_dict()
    }
    
    # 初始化插件
    fastapi_plugin.initialize(plugin_config)
    
    logger.success("FastAPI插件配置完成")
    logger.info("插件信息:")
    
    # 显示插件信息
    info = fastapi_plugin.get_info()
    for key, value in info.items():
        if key == "server_info":
            logger.info(f"  服务器信息:")
            for k, v in value.items():
                logger.info(f"    {k}: {v}")
        elif key == "features":
            logger.info(f"  功能特性:")
            for feature in value:
                logger.info(f"    - {feature}")
        else:
            logger.info(f"  {key}: {value}")
    
    print("\n要启动服务器，请运行:")
    print("poetry run python examples/fastapi_plugin_example.py --start")
    
    return fastapi_plugin


def demo_custom_plugin():
    """自定义插件演示"""
    print("\n=== 自定义插件演示 ===\n")
    
    from wp_python.plugin.base import BasePlugin
    from fastapi import APIRouter
    
    class CustomPlugin(BasePlugin):
        """自定义插件示例"""
        
        def __init__(self):
            super().__init__("custom_demo", "1.0.0")
            self.router = APIRouter()
            self._setup_routes()
        
        def _setup_routes(self):
            """设置自定义路由"""
            
            @self.router.get("/custom/hello")
            async def hello():
                return {"message": "Hello from custom plugin!"}
            
            @self.router.get("/custom/status")
            async def status():
                return {
                    "plugin": self.name,
                    "version": self.version,
                    "status": "running"
                }
        
        def initialize(self, config=None):
            """初始化插件"""
            self.logger.info("自定义插件初始化")
        
        def start(self):
            """启动插件"""
            self.logger.success("自定义插件启动")
        
        def stop(self):
            """停止插件"""
            self.logger.info("自定义插件停止")
        
        def get_router(self):
            """获取路由器"""
            return self.router
    
    # 创建自定义插件
    custom_plugin = CustomPlugin()
    
    # 获取插件管理器
    plugin_manager = get_plugin_manager()
    
    # 注册自定义插件
    plugin_manager.register(custom_plugin)
    
    # 初始化插件
    custom_plugin.initialize()
    custom_plugin.enable()
    
    print("自定义插件创建完成！")
    print("插件信息:", custom_plugin.get_info())
    
    return custom_plugin


def start_server():
    """启动服务器"""
    print("=== 启动FastAPI服务器 ===\n")
    
    # 设置日志
    logger = setup_logging(level="DEBUG")
    
    # 获取插件管理器
    plugin_manager = get_plugin_manager()
    
    # 创建并配置FastAPI插件
    fastapi_plugin = FastAPIPlugin()
    plugin_manager.register(fastapi_plugin)
    
    # 创建自定义插件
    custom_plugin = demo_custom_plugin()
    
    # 获取配置
    config = get_config('.env.dev')
    
    # 配置FastAPI插件
    plugin_config = {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": True,
        "reload": True,
        "title": "WordPress REST API 服务",
        "description": "基于wp-python的WordPress REST API FastAPI服务",
        "version": "1.0.0",
        "cors_origins": ["*"],
        "wordpress_config": config.to_dict()
    }
    
    # 初始化插件
    fastapi_plugin.initialize(plugin_config)
    
    # 添加自定义路由
    if hasattr(custom_plugin, 'get_router'):
        fastapi_plugin.add_custom_route(custom_plugin.get_router())
        logger.info("已添加自定义插件路由")
    
    # 启动服务器
    logger.success("正在启动FastAPI服务器...")
    logger.info("可用端点:")
    logger.info("  - API文档: http://localhost:8000/docs")
    logger.info("  - ReDoc文档: http://localhost:8000/redoc")
    logger.info("  - API根: http://localhost:8000/api/v1/")
    logger.info("  - 健康检查: http://localhost:8000/api/v1/health")
    logger.info("  - 文章列表: http://localhost:8000/api/v1/posts")
    logger.info("  - 自定义端点: http://localhost:8000/custom/hello")
    
    try:
        # 启动插件
        fastapi_plugin.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务器...")
        fastapi_plugin.stop()
        plugin_manager.stop_all()


def demo_production_deployment():
    """生产环境部署演示"""
    print("\n=== 生产环境部署演示 ===\n")
    
    print("生产环境部署配置:")
    print("""
# 1. 使用正式环境配置
config = get_config('.env')  # 使用 .env 文件

# 2. 生产环境插件配置
plugin_config = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": False,          # 关闭调试模式
    "reload": False,         # 关闭热重载
    "workers": 4,            # 多进程
    "title": "WordPress API",
    "docs_url": None,        # 关闭文档（可选）
    "redoc_url": None,       # 关闭ReDoc（可选）
    "cors_origins": ["https://your-domain.com"],  # 限制CORS
    "wordpress_config": config.to_dict()
}

# 3. 启动生产服务器
fastapi_plugin.initialize(plugin_config)
fastapi_plugin.start()  # 自动使用Gunicorn
""")
    
#     print("Docker部署示例:")
#     print("""
# # Dockerfile
# FROM python:3.11-slim

# WORKDIR /app
# COPY . .

# RUN pip install poetry
# RUN poetry install --no-dev

# EXPOSE 8000

# CMD ["poetry", "run", "python", "your_app.py"]
# """)


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--start":
        start_server()
    else:
        # 演示基础功能
        demo_basic_usage()
        demo_custom_plugin()
        demo_production_deployment()
        
        print("\n=== FastAPI插件演示完成 ===")
        print("\n使用说明:")
        print("1. 基础使用: poetry run python examples/fastapi_plugin_example.py")
        print("2. 启动服务器: poetry run python examples/fastapi_plugin_example.py --start")
        print("3. 访问API文档: http://localhost:8000/docs")


if __name__ == "__main__":
    main()