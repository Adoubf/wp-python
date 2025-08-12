"""
WordPress REST API 日志系统

使用 rich + logging 提供美观的日志输出和文件记录。
"""

import logging
import os
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install


class WordPressLogger:
    """WordPress API 专用日志器"""
    
    def __init__(
        self,
        name: str = "wp_python",
        level: str = "INFO",
        log_file: Optional[str] = None,
        console_output: bool = True
    ):
        """
        初始化日志器
        
        参数:
            name: 日志器名称
            level: 日志级别
            log_file: 日志文件路径
            console_output: 是否输出到控制台
        """
        self.name = name
        self.level = getattr(logging, level.upper())
        self.log_file = log_file
        self.console_output = console_output
        
        # 安装rich异常处理
        install(show_locals=True)
        
        # 创建控制台
        self.console = Console()
        
        # 设置日志器
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志器"""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        
        # 清除现有处理器
        logger.handlers.clear()
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 控制台处理器（使用Rich）
        if self.console_output:
            console_handler = RichHandler(
                console=self.console,
                show_time=True,
                show_path=False,  # 关闭路径显示，简化输出
                markup=True,
                rich_tracebacks=True,
                omit_repeated_times=False,
                log_time_format="[%H:%M:%S]"  # 简化时间格式
            )
            console_handler.setLevel(self.level)
            logger.addHandler(console_handler)
        
        # 文件处理器
        if self.log_file:
            # 确保日志目录存在
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        self.logger.debug(f"🐛 {message}", **kwargs)
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        self.logger.info(f"ℹ️  {message}", **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        self.logger.warning(f"⚠️  {message}", **kwargs)
    
    def error(self, message: str, **kwargs):
        """错误日志"""
        self.logger.error(f"❌ {message}", **kwargs)
    
    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self.logger.critical(f"🚨 {message}", **kwargs)
    
    def success(self, message: str):
        """成功日志（使用Rich样式）"""
        self.logger.info(f"✅ {message}")
    
    def failure(self, message: str):
        """失败日志（使用Rich样式）"""
        self.logger.error(f"❌ {message}")
    
    def progress(self, message: str):
        """进度日志（使用Rich样式）"""
        self.logger.info(f"🔄 {message}")


# 全局日志器实例
_logger_instance: Optional[WordPressLogger] = None


def get_logger(
    name: str = "wp_python",
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> WordPressLogger:
    """
    获取全局日志器实例
    
    参数:
        name: 日志器名称
        level: 日志级别
        log_file: 日志文件路径
        console_output: 是否输出到控制台
        
    返回:
        日志器实例
    """
    global _logger_instance
    
    if _logger_instance is None:
        # 从环境变量获取默认配置
        level = level or os.getenv('LOG_LEVEL', 'INFO')
        log_file = log_file or os.getenv('LOG_FILE')
        
        _logger_instance = WordPressLogger(
            name=name,
            level=level,
            log_file=log_file,
            console_output=console_output
        )
    
    return _logger_instance


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True
) -> WordPressLogger:
    """
    设置全局日志配置
    
    参数:
        level: 日志级别
        log_file: 日志文件路径
        console_output: 是否输出到控制台
        
    返回:
        配置好的日志器
    """
    global _logger_instance
    _logger_instance = WordPressLogger(
        level=level,
        log_file=log_file,
        console_output=console_output
    )
    return _logger_instance