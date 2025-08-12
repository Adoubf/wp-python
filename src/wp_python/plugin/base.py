"""
WordPress REST API 插件基类

定义插件系统的基础架构，支持用户自定义插件开发。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import inspect
from ..utils.logger import get_logger


class BasePlugin(ABC):
    """
    插件基类
    
    所有插件都应该继承此类并实现必要的方法。
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        初始化插件
        
        参数:
            name: 插件名称
            version: 插件版本
        """
        self.name = name
        self.version = version
        self.enabled = False
        self.logger = get_logger(f"plugin.{name}")
        self._config: Dict[str, Any] = {}
    
    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化插件
        
        参数:
            config: 插件配置
        """
        pass
    
    @abstractmethod
    def start(self) -> None:
        """启动插件"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止插件"""
        pass
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        配置插件
        
        参数:
            config: 配置字典
        """
        self._config.update(config)
        self.logger.debug(f"插件 {self.name} 配置已更新: {config}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        参数:
            key: 配置键
            default: 默认值
            
        返回:
            配置值
        """
        return self._config.get(key, default)
    
    def enable(self) -> None:
        """启用插件"""
        if not self.enabled:
            self.enabled = True
            self.logger.success(f"插件 {self.name} 已启用")
    
    def disable(self) -> None:
        """禁用插件"""
        if self.enabled:
            self.enabled = False
            self.logger.warning(f"插件 {self.name} 已禁用")
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取插件信息
        
        返回:
            插件信息字典
        """
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "class": self.__class__.__name__,
            "module": self.__class__.__module__
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name} v{self.version} ({'启用' if self.enabled else '禁用'})"


class PluginManager:
    """
    插件管理器
    
    负责插件的注册、加载、启动和管理。
    """
    
    def __init__(self):
        """初始化插件管理器"""
        self.plugins: Dict[str, BasePlugin] = {}
        self.logger = get_logger("plugin_manager")
    
    def register(self, plugin: BasePlugin) -> None:
        """
        注册插件
        
        参数:
            plugin: 插件实例
        """
        if not isinstance(plugin, BasePlugin):
            raise TypeError("插件必须继承自 BasePlugin")
        
        if plugin.name in self.plugins:
            self.logger.warning(f"插件 {plugin.name} 已存在，将被覆盖")
        
        self.plugins[plugin.name] = plugin
        self.logger.info(f"插件 {plugin.name} 已注册")
    
    def unregister(self, name: str) -> None:
        """
        注销插件
        
        参数:
            name: 插件名称
        """
        if name in self.plugins:
            plugin = self.plugins[name]
            if plugin.enabled:
                plugin.stop()
                plugin.disable()
            del self.plugins[name]
            self.logger.info(f"插件 {name} 已注销")
        else:
            self.logger.warning(f"插件 {name} 不存在")
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        获取插件实例
        
        参数:
            name: 插件名称
            
        返回:
            插件实例或None
        """
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        列出所有插件
        
        返回:
            插件信息列表
        """
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def enable_plugin(self, name: str) -> bool:
        """
        启用插件
        
        参数:
            name: 插件名称
            
        返回:
            是否成功启用
        """
        plugin = self.get_plugin(name)
        if plugin:
            try:
                plugin.enable()
                plugin.start()
                return True
            except Exception as e:
                self.logger.error(f"启用插件 {name} 失败: {e}")
                return False
        else:
            self.logger.error(f"插件 {name} 不存在")
            return False
    
    def disable_plugin(self, name: str) -> bool:
        """
        禁用插件
        
        参数:
            name: 插件名称
            
        返回:
            是否成功禁用
        """
        plugin = self.get_plugin(name)
        if plugin:
            try:
                plugin.stop()
                plugin.disable()
                return True
            except Exception as e:
                self.logger.error(f"禁用插件 {name} 失败: {e}")
                return False
        else:
            self.logger.error(f"插件 {name} 不存在")
            return False
    
    def initialize_all(self, config: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """
        初始化所有插件
        
        参数:
            config: 插件配置字典，键为插件名，值为配置
        """
        config = config or {}
        
        for name, plugin in self.plugins.items():
            try:
                plugin_config = config.get(name, {})
                plugin.initialize(plugin_config)
                self.logger.info(f"插件 {name} 初始化成功")
            except Exception as e:
                self.logger.error(f"插件 {name} 初始化失败: {e}")
    
    def start_all(self) -> None:
        """启动所有已启用的插件"""
        for plugin in self.plugins.values():
            if plugin.enabled:
                try:
                    plugin.start()
                    self.logger.info(f"插件 {plugin.name} 启动成功")
                except Exception as e:
                    self.logger.error(f"插件 {plugin.name} 启动失败: {e}")
    
    def stop_all(self) -> None:
        """停止所有插件"""
        for plugin in self.plugins.values():
            if plugin.enabled:
                try:
                    plugin.stop()
                    self.logger.info(f"插件 {plugin.name} 停止成功")
                except Exception as e:
                    self.logger.error(f"插件 {plugin.name} 停止失败: {e}")
    
    def auto_discover(self, package_name: str) -> None:
        """
        自动发现并注册插件
        
        参数:
            package_name: 包名
        """
        try:
            import importlib
            import pkgutil
            
            package = importlib.import_module(package_name)
            
            for _, module_name, _ in pkgutil.iter_modules(package.__path__, package_name + "."):
                try:
                    module = importlib.import_module(module_name)
                    
                    # 查找继承自BasePlugin的类
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, BasePlugin) and 
                            obj != BasePlugin and 
                            obj.__module__ == module_name):
                            
                            # 自动实例化并注册插件
                            plugin_instance = obj()
                            self.register(plugin_instance)
                            
                except Exception as e:
                    self.logger.warning(f"加载模块 {module_name} 失败: {e}")
                    
        except Exception as e:
            self.logger.error(f"自动发现插件失败: {e}")


# 全局插件管理器实例
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """
    获取全局插件管理器实例
    
    返回:
        插件管理器实例
    """
    global _plugin_manager
    
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    
    return _plugin_manager