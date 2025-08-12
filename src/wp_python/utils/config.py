"""
WordPress REST API 配置管理

从环境变量和.env文件加载配置信息。
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class WordPressConfig:
    """WordPress配置管理器"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置管理器
        
        参数:
            env_file: 环境文件路径，默认为.env（正式环境）
                     可选值：.env（正式环境）、.env.dev（开发环境）
        """
        self.env_file = env_file or ".env"
        self.is_dev = self.env_file.endswith('.dev')
        self._load_env()
    
    def _load_env(self):
        """加载环境变量"""
        # 查找环境文件
        env_path = Path(self.env_file)
        if not env_path.exists():
            # 尝试在项目根目录查找
            root_env_path = Path.cwd() / self.env_file
            if root_env_path.exists():
                env_path = root_env_path
        
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ 已加载环境配置: {env_path}")
        else:
            print(f"⚠️  未找到环境文件: {self.env_file}")
    
    @property
    def base_url(self) -> str:
        """WordPress站点URL"""
        return os.getenv('WP_BASE_URL', 'https://your-wordpress-site.com')
    
    @property
    def username(self) -> Optional[str]:
        """用户名"""
        return os.getenv('WP_USERNAME')
    
    @property
    def password(self) -> Optional[str]:
        """密码"""
        return os.getenv('WP_PASSWORD')
    
    @property
    def app_password(self) -> Optional[str]:
        """应用程序密码"""
        return os.getenv('WP_APP_PASSWORD')
    
    @property
    def jwt_token(self) -> Optional[str]:
        """JWT令牌"""
        return os.getenv('WP_JWT_TOKEN')
    
    @property
    def timeout(self) -> int:
        """请求超时时间"""
        return int(os.getenv('WP_TIMEOUT', '30'))
    
    @property
    def verify_ssl(self) -> bool:
        """是否验证SSL"""
        return os.getenv('WP_VERIFY_SSL', 'true').lower() == 'true'
    
    @property
    def log_level(self) -> str:
        """日志级别"""
        # 开发环境默认DEBUG，正式环境默认INFO
        default_level = 'DEBUG' if self.is_dev else 'INFO'
        return os.getenv('LOG_LEVEL', default_level)
    
    @property
    def debug(self) -> bool:
        """是否开启调试模式"""
        # 开发环境默认开启调试
        default_debug = 'true' if self.is_dev else 'false'
        return os.getenv('DEBUG', default_debug).lower() == 'true'
    
    @property
    def environment(self) -> str:
        """当前环境"""
        return 'development' if self.is_dev else 'production'
    
    @property
    def log_file(self) -> Optional[str]:
        """日志文件路径"""
        return os.getenv('LOG_FILE')
    
    @property
    def test_post_id(self) -> int:
        """测试文章ID"""
        return int(os.getenv('TEST_POST_ID', '1'))
    
    @property
    def test_category_id(self) -> int:
        """测试分类ID"""
        return int(os.getenv('TEST_CATEGORY_ID', '1'))
    
    @property
    def test_tag_id(self) -> int:
        """测试标签ID"""
        return int(os.getenv('TEST_TAG_ID', '1'))
    
    @property
    def test_user_id(self) -> int:
        """测试用户ID"""
        return int(os.getenv('TEST_USER_ID', '1'))
    
    def get_auth_config(self) -> Dict[str, Any]:
        """获取认证配置"""
        config = {}
        
        if self.username:
            config['username'] = self.username
        
        if self.app_password:
            config['app_password'] = self.app_password
        elif self.password:
            config['password'] = self.password
        
        if self.jwt_token:
            config['jwt_token'] = self.jwt_token
        
        return config
    
    def get_client_config(self) -> Dict[str, Any]:
        """获取客户端配置"""
        return {
            'timeout': self.timeout,
            'verify_ssl': self.verify_ssl
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'environment': self.environment,
            'base_url': self.base_url,
            'username': self.username,
            'has_password': bool(self.password),
            'has_app_password': bool(self.app_password),
            'has_jwt_token': bool(self.jwt_token),
            'timeout': self.timeout,
            'verify_ssl': self.verify_ssl,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'debug': self.debug
        }


# 全局配置实例
_config_instance: Optional[WordPressConfig] = None


def get_config(env_file: Optional[str] = None) -> WordPressConfig:
    """
    获取全局配置实例
    
    参数:
        env_file: 环境文件路径
        
    返回:
        配置实例
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = WordPressConfig(env_file)
    
    return _config_instance


def load_config(env_file: Optional[str] = None) -> WordPressConfig:
    """
    加载配置
    
    参数:
        env_file: 环境文件路径
        
    返回:
        配置实例
    """
    global _config_instance
    _config_instance = WordPressConfig(env_file)
    return _config_instance