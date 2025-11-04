# /astrbot_plugin_class2_notify/config.py

import os
import json
from collections.abc import Mapping
from astrbot.core import logger


class PluginConfig:
    def __init__(
        self,
        config_file_path: str,
        initial_data=None,
    ):
        # 默认配置
        self.api_domain = ""
        self.api_token = ""
        self.check_interval = 5  # 分钟
        self.notify_groups = []
        self.enable_notification = True
        self.sign_status_filter = [0, 1, 2]  # 默认显示未上架、未开始、进行中
        self._data = {}

        if initial_data is not None:
            self.merge(initial_data)

        self._load_from_file(config_file_path)
        self._sync_config()

    def _load_from_file(self, config_file_path: str) -> None:
        try:
            with open(config_file_path, "r", encoding="utf-8-sig") as f:
                config = json.load(f)
                self._merge_data(config)
        except FileNotFoundError:
            logger.warning("第二课堂插件配置文件未找到，将使用默认配置。")
        except Exception as e:
            logger.error(f"加载第二课堂插件配置文件时出错: {e}")

    def _merge_data(self, data) -> None:
        if data is None:
            return

        if isinstance(data, PluginConfig):
            candidate = data.to_dict()
        elif isinstance(data, Mapping):
            candidate = dict(data)
        elif hasattr(data, "__dict__"):
            candidate = {k: v for k, v in vars(data).items() if not k.startswith("_")}
        else:
            return

        self._data.update(candidate)

    def _sync_config(self) -> None:
        """同步配置到属性"""
        self.api_domain = self._data.get("api_domain", self.api_domain)
        self.api_token = self._data.get("api_token", self.api_token)
        self.check_interval = self._data.get("check_interval", self.check_interval)
        self.notify_groups = self._data.get("notify_groups", self.notify_groups)
        self.enable_notification = self._data.get("enable_notification", self.enable_notification)
        self.sign_status_filter = self._data.get("sign_status_filter", self.sign_status_filter)

    def merge(self, data) -> None:
        self._merge_data(data)
        self._sync_config()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def to_dict(self) -> dict:
        return {
            "api_domain": self.api_domain,
            "api_token": self.api_token,
            "check_interval": self.check_interval,
            "notify_groups": self.notify_groups,
            "enable_notification": self.enable_notification,
            "sign_status_filter": self.sign_status_filter,
        }


def load_config(context, runtime_config=None) -> PluginConfig:
    """加载插件配置"""
    plugin_config_path = os.path.join(
        "data", "config", "astrbot_plugin_class2_notify_config.json"
    )
    p_config = PluginConfig(plugin_config_path, runtime_config)

    return p_config
