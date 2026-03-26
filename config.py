"""neo_minimax_tts 插件配置。

配置 MiniMax TTS API 相关参数。
配置文件默认路径：config/plugins/neo_minimax_tts/config.toml
"""

from __future__ import annotations

from typing import ClassVar

from src.core.components.base.config import BaseConfig, Field, SectionBase, config_section


class NeoMiniMaxTTSConfig(BaseConfig):
    """neo_minimax_tts 插件配置。"""

    config_name: ClassVar[str] = "config"
    config_description: ClassVar[str] = "Neo-MiniMax-TTS 文本转语音插件配置"

    @config_section("minimax")
    class MiniMaxSection(SectionBase):
        """MiniMax TTS API 配置。"""

        api_key: str = Field(
            default="",
            description="MiniMax API Key（必填）",
        )

        model: str = Field(
            default="speech-2.8-hd",
            description="TTS 模型名称（speech-2.8-hd, speech-2.8-turbo）",
        )

        voice_id: str = Field(
            default="female-tianmei",
            description="语音 ID（female-tianmei, female-yujie, male-qn-qingse 等，支持声音克隆）",
        )

        speed: float = Field(
            default=1.0,
            description="语速（0.5-2.0，默认 1.0）",
        )

        volume: float = Field(
            default=1.0,
            description="音量（0.1-1.0，默认 1.0）",
        )

    @config_section("output")
    class OutputSection(SectionBase):
        """输出配置。"""

        audio_dir: str = Field(
            default="data/neo_minimax_tts/audio",
            description="音频文件保存目录",
        )

        audio_format: str = Field(
            default="mp3",
            description="音频格式（mp3, wav, aac）",
        )

        max_text_length: int = Field(
            default=500,
            description="单次转换最大文本长度（字符数）",
        )

    @config_section("behavior")
    class BehaviorSection(SectionBase):
        """行为配置。"""

        auto_delete: bool = Field(
            default=False,
            description="发送后是否自动删除本地音频文件",
        )

        send_as_record: bool = Field(
            default=True,
            description="是否以语音消息形式发送（false 则发送文件）",
        )

    @config_section("plugin")
    class PluginSection(SectionBase):
        """插件行为配置。"""

        inject_system_prompt: bool = Field(
            default=True,
            description="是否注入系统提示词（告知 LLM 使用语音功能）",
        )

    minimax: MiniMaxSection = Field(default_factory=MiniMaxSection)
    output: OutputSection = Field(default_factory=OutputSection)
    behavior: BehaviorSection = Field(default_factory=BehaviorSection)
    plugin: PluginSection = Field(default_factory=PluginSection)
