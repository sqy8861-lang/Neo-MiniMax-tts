"""neo_minimax_tts Action：将文本转换为语音并发送。

该 Action 面向 LLM Tool Calling：
- 输入：要转换为语音的文本
- 行为：调用 MiniMax TTS API 生成语音文件并发送
"""

from __future__ import annotations

from typing import Annotated, cast

from src.app.plugin_system.api.send_api import send_audio, send_file
from src.core.components.base.action import BaseAction

from .service import NeoMiniMaxTTSService


class NeoMiniMaxTTSAction(BaseAction):
    """文本转语音动作。"""

    action_name: str = "neo_minimax_tts"
    action_description: str = "将文本转换为语音消息并发送。适用于需要以语音形式回复的场景，如问候、重要提醒、情感表达等。语音消息比文字更生动，能更好地传达语气和情感。支持使用声音克隆音色，只需提供克隆后的 voice_id。"
    primary_action: bool = False

    async def execute(
        self,
        text: Annotated[str, "要转换为语音的文本内容"],
        voice_id: Annotated[
            str | None,
            "可选的语音 ID（覆盖配置文件中的设置，支持使用声音克隆音色）",
        ] = None,
    ) -> tuple[bool, str]:
        """执行文本转语音动作。"""
        from src.app.plugin_system.api.service_api import get_service

        service = get_service("neo_minimax_tts:service:neo_minimax_tts")
        if service is None:
            return False, "neo_minimax_tts service 未加载"

        service = cast(NeoMiniMaxTTSService, service)

        cfg = service._cfg()
        ok, result, audio_path = await service.text_to_speech(
            text, save_to_file=True, voice_id=voice_id
        )

        if not ok:
            return False, result

        if not audio_path:
            return False, "音频文件生成失败"

        try:
            if cfg.behavior.send_as_record:
                await send_audio(
                    stream_id=self.chat_stream.stream_id,
                    platform=self.chat_stream.platform,
                    audio_path=audio_path,
                )
            else:
                await send_file(
                    stream_id=self.chat_stream.stream_id,
                    platform=self.chat_stream.platform,
                    file_path=audio_path,
                )

            if cfg.behavior.auto_delete:
                service.cleanup_audio_file(audio_path)

            return True, f"已发送语音消息: {result}"

        except Exception as e:
            return False, f"发送语音消息失败: {str(e)}"
