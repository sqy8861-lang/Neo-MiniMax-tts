"""neo_minimax_tts 服务实现。

提供 MiniMax TTS API 调用功能，将文本转换为语音文件。
"""

from __future__ import annotations

import base64
import hashlib
import io
import time
from pathlib import Path
from typing import Any

import aiohttp

from src.core.components.base.service import BaseService
from src.kernel.logger import get_logger

from .config import NeoMiniMaxTTSConfig

logger = get_logger("neo_minimax_tts")


class NeoMiniMaxTTSService(BaseService):
    """文本转语音服务。

    对外提供：
    - text_to_speech：将文本转换为语音文件
    - get_audio_file：获取生成的音频文件路径
    """

    service_name: str = "neo_minimax_tts"
    service_description: str = "MiniMax 文本转语音服务"
    version: str = "1.0.0"

    def _cfg(self) -> NeoMiniMaxTTSConfig:
        """获取插件配置实例。"""
        cfg = self.plugin.config
        if not isinstance(cfg, NeoMiniMaxTTSConfig):
            raise RuntimeError("neo_minimax_tts plugin config 未正确加载")
        return cfg

    def _audio_dir(self) -> Path:
        """获取音频文件保存目录。"""
        path = Path(self._cfg().output.audio_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _get_audio_format(self) -> str:
        """获取音频格式。"""
        return self._cfg().output.audio_format.lower()

    def _generate_audio_filename(self, text: str) -> str:
        """根据文本内容生成唯一的音频文件名。"""
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:16]
        timestamp = int(time.time())
        return f"tts_{timestamp}_{text_hash}.{self._get_audio_format()}"

    async def _call_minimax_tts(
        self,
        text: str,
        voice_id: str | None = None,
    ) -> bytes:
        """调用 MiniMax TTS API。

        Args:
            text: 要转换的文本
            voice_id: 可选的语音 ID（覆盖配置文件中的设置，支持声音克隆音色）

        Returns:
            音频文件的二进制数据

        Raises:
            RuntimeError: API 调用失败时
        """
        cfg = self._cfg()

        if not cfg.minimax.api_key:
            raise RuntimeError("MiniMax API Key 未配置，请在配置文件中设置 minimax.api_key")

        # group_id 是可选的

        url = "https://api.minimax.chat/v1/text_to_speech"

        headers = {
            "Authorization": f"Bearer {cfg.minimax.api_key}",
            "Content-Type": "application/json",
        }

        use_voice_id = voice_id if voice_id else cfg.minimax.voice_id

        payload = {
            "model": cfg.minimax.model,
            "text": text,
            "voice_id": use_voice_id,
            "speed": cfg.minimax.speed,
            "volume": cfg.minimax.volume,
        }

        logger.debug(f"调用 MiniMax TTS API: 文本长度={len(text)}, 模型={cfg.minimax.model}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise RuntimeError(
                            f"MiniMax TTS API 调用失败 (状态码 {response.status}): {error_text}"
                        )

                    content_type = response.headers.get("Content-Type", "")
                    if "audio" not in content_type and "application/json" in content_type:
                        error_data = await response.json()
                        raise RuntimeError(f"MiniMax TTS API 返回错误: {error_data}")

                    audio_data = await response.read()
                    logger.info(f"MiniMax TTS 调用成功: 音频大小={len(audio_data)} 字节")
                    return audio_data

        except aiohttp.ClientError as e:
            raise RuntimeError(f"MiniMax TTS API 网络请求失败: {e}") from e
        except Exception as e:
            raise RuntimeError(f"MiniMax TTS API 调用异常: {e}") from e

    async def text_to_speech(
        self,
        text: str,
        save_to_file: bool = True,
        voice_id: str | None = None,
    ) -> tuple[bool, str, str | None]:
        """将文本转换为语音。

        Args:
            text: 要转换的文本
            save_to_file: 是否保存到文件
            voice_id: 可选的语音 ID（覆盖配置文件中的设置，支持声音克隆音色）

        Returns:
            (是否成功, 结果消息, 音频文件路径)
        """
        cfg = self._cfg()

        if not text or not text.strip():
            return False, "文本内容为空", None

        text = text.strip()

        if len(text) > cfg.output.max_text_length:
            return (
                False,
                f"文本长度超过限制（{len(text)} > {cfg.output.max_text_length}）",
                None,
            )

        try:
            audio_data = await self._call_minimax_tts(text, voice_id=voice_id)

            if not save_to_file:
                return True, "语音转换成功（未保存文件）", None

            audio_dir = self._audio_dir()
            filename = self._generate_audio_filename(text)
            audio_path = audio_dir / filename

            audio_path.write_bytes(audio_data)
            logger.info(f"音频文件已保存: {audio_path}")

            return True, f"语音转换成功，文件: {filename}", str(audio_path)

        except Exception as e:
            logger.error(f"文本转语音失败: {e}", exc_info=e)
            return False, f"转换失败: {str(e)}", None

    async def text_to_speech_base64(
        self,
        text: str,
        voice_id: str | None = None,
    ) -> tuple[bool, str, str | None]:
        """将文本转换为语音并返回 base64 编码。

        Args:
            text: 要转换的文本
            voice_id: 可选的语音 ID（覆盖配置文件中的设置，支持声音克隆音色）

        Returns:
            (是否成功, 结果消息, base64 编码的音频数据)
        """
        if not text or not text.strip():
            return False, "文本内容为空", None

        text = text.strip()
        cfg = self._cfg()

        if len(text) > cfg.output.max_text_length:
            return (
                False,
                f"文本长度超过限制（{len(text)} > {cfg.output.max_text_length}）",
                None,
            )

        try:
            audio_data = await self._call_minimax_tts(text, voice_id=voice_id)

            audio_format = self._get_audio_format()
            mime_type = {
                "mp3": "audio/mpeg",
                "wav": "audio/wav",
                "aac": "audio/aac",
            }.get(audio_format, "audio/mpeg")

            base64_data = base64.b64encode(audio_data).decode("utf-8")
            data_uri = f"data:{mime_type};base64,{base64_data}"

            return True, "语音转换成功", data_uri

        except Exception as e:
            logger.error(f"文本转语音失败: {e}", exc_info=e)
            return False, f"转换失败: {str(e)}", None

    def cleanup_audio_file(self, audio_path: str) -> bool:
        """删除音频文件。

        Args:
            audio_path: 音频文件路径

        Returns:
            是否删除成功
        """
        try:
            path = Path(audio_path)
            if path.exists() and path.is_file():
                path.unlink()
                logger.debug(f"音频文件已删除: {audio_path}")
                return True
            return False
        except Exception as e:
            logger.warning(f"删除音频文件失败: {e}")
            return False
