"""neo_minimax_tts 插件入口。

加载后注册文本转语音服务，提供 Action 组件供 LLM 调用。
"""

from __future__ import annotations

from src.core.components import BasePlugin, register_plugin
from src.kernel.logger import get_logger

from .action import NeoMiniMaxTTSAction
from .config import NeoMiniMaxTTSConfig
from .service import NeoMiniMaxTTSService

logger = get_logger("neo_minimax_tts")


@register_plugin
class NeoMiniMaxTTSPlugin(BasePlugin):
    """neo_minimax_tts 插件。"""

    plugin_name: str = "neo_minimax_tts"
    plugin_description: str = "基于 MiniMax 的文本转语音插件，支持声音克隆和手动触发语音消息发送"
    plugin_version: str = "1.0.0"

    configs: list[type] = [NeoMiniMaxTTSConfig]
    dependent_components: list[str] = []

    def __init__(self, config: NeoMiniMaxTTSConfig | None = None) -> None:
        super().__init__(config)

    def get_components(self) -> list[type]:
        """返回本插件提供的组件类。"""
        return [NeoMiniMaxTTSService, NeoMiniMaxTTSAction]

    async def on_plugin_loaded(self) -> None:
        """插件加载完成后：初始化配置。"""
        logger.info("neo_minimax_tts 插件已加载")

        cfg = self.config
        if isinstance(cfg, NeoMiniMaxTTSConfig):
            if not cfg.minimax.api_key:
                logger.warning(
                    "MiniMax API Key 未配置，请在 config/plugins/neo_minimax_tts/config.toml 中设置 minimax.api_key"
                )
            if not cfg.minimax.group_id:
                logger.warning(
                    "MiniMax Group ID 未配置，请在 config/plugins/neo_minimax_tts/config.toml 中设置 minimax.group_id"
                )

    async def on_plugin_unloaded(self) -> None:
        """插件卸载前：清理资源。"""
        logger.info("neo_minimax_tts 插件已卸载")
