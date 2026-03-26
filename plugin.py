"""neo_minimax_tts 插件入口。

加载后注册文本转语音服务，提供 Action 组件供 LLM 调用。
"""

from __future__ import annotations

from typing import Any

from src.core.components import BasePlugin, register_plugin
from src.kernel.logger import get_logger

from .action import NeoMiniMaxTTSAction
from .config import NeoMiniMaxTTSConfig
from .service import NeoMiniMaxTTSService

logger = get_logger("neo_minimax_tts")


_TARGET_REMINDER_BUCKET = "actor"
_TARGET_REMINDER_NAME = "关于语音消息的使用"
_TTS_USAGE_REMINDER = (
    '你拥有语音消息功能，可以将文字转换为语音发送给用户。'
    '语音消息比文字更生动，能更好地传达语气和情感。'
    '默认情况下，你会使用配置文件中预设的克隆音色进行语音生成。'
    '当用户表达类似"想听你的声音"、"请对我说"、"用语音说"等意愿时，'
    '请记得使用语音消息功能进行回复。'
    '语音消息功能在你的日常互动中扮演着重要角色，请你牢记并认真对待。'
)


def build_tts_actor_reminder(plugin: Any) -> str:
    """构建 neo_minimax_tts 的 actor reminder。"""
    config = getattr(plugin, "config", None)
    if isinstance(config, NeoMiniMaxTTSConfig):
        if not config.plugin.inject_system_prompt:
            return ""
    return _TTS_USAGE_REMINDER


def sync_tts_actor_reminder(plugin: Any) -> str:
    """同步 neo_minimax_tts 的 actor reminder。"""
    from src.core.prompt import get_system_reminder_store

    store = get_system_reminder_store()
    reminder_content = build_tts_actor_reminder(plugin)
    if not reminder_content:
        store.delete(_TARGET_REMINDER_BUCKET, _TARGET_REMINDER_NAME)
        logger.debug("neo_minimax_tts actor reminder 已清理")
        return ""

    store.set(
        _TARGET_REMINDER_BUCKET,
        name=_TARGET_REMINDER_NAME,
        content=reminder_content,
    )
    logger.debug("neo_minimax_tts actor reminder 已同步")
    return reminder_content


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
        """插件加载完成后：初始化配置并同步系统提示词。"""
        sync_tts_actor_reminder(self)
        logger.info("neo_minimax_tts 插件已加载")

        cfg = self.config
        if isinstance(cfg, NeoMiniMaxTTSConfig):
            if not cfg.minimax.api_key:
                logger.warning(
                    "MiniMax API Key 未配置，请在 config/plugins/neo_minimax_tts/config.toml 中设置 minimax.api_key"
                )

    async def on_plugin_unloaded(self) -> None:
        """插件卸载前：清理资源和系统提示词。"""
        from src.core.prompt import get_system_reminder_store

        get_system_reminder_store().delete(_TARGET_REMINDER_BUCKET, _TARGET_REMINDER_NAME)
        logger.info("neo_minimax_tts 插件已卸载")
