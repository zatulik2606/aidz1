from io import BytesIO

import base64
from openai import AsyncOpenAI

from src.config import Config


def _normalize_audio_format(mime_type: str = "") -> str:
    normalized_mime = mime_type.strip().lower()
    mime_to_format = {
        "audio/ogg": "ogg",
        "audio/mpeg": "mp3",
        "audio/mp3": "mp3",
        "audio/wav": "wav",
        "audio/x-wav": "wav",
        "audio/aac": "aac",
        "audio/flac": "flac",
        "audio/x-flac": "flac",
        "audio/mp4": "m4a",
        "audio/x-m4a": "m4a",
    }
    return mime_to_format.get(normalized_mime, "ogg")


async def generate_audio_reply(
    audio_bytes: bytes,
    config: Config,
    audio_format: str = "ogg",
) -> str:
    client = AsyncOpenAI(
        api_key=config.llm_api_key,
        base_url=config.llm_base_url,
    )
    def _build_audio_buffer() -> BytesIO:
        buffer = BytesIO(audio_bytes)
        buffer.name = f"voice.{audio_format}"
        return buffer

    try:
        transcript = await client.audio.transcriptions.create(
            model=config.llm_transcribe_model,
            file=_build_audio_buffer(),
            prompt=config.system_prompt_audio,
            language="ru",
        )
        text = getattr(transcript, "text", "").strip()
        if text:
            return text
    except Exception:
        pass

    try:
        fallback_transcript = await client.audio.transcriptions.create(
            model="openai/whisper-1",
            file=_build_audio_buffer(),
            prompt=config.system_prompt_audio,
            language="ru",
        )
        fallback_text = getattr(fallback_transcript, "text", "").strip()
        if fallback_text:
            return fallback_text
    except Exception:
        pass

    encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")
    response = await client.chat.completions.create(
        model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        messages=[
            {
                "role": "system",
                "content": (
                    "Сделай транскрипцию аудио. "
                    "Верни только распознанный текст, без комментариев."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Транскрибируй это аудио."},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": encoded_audio,
                            "format": audio_format,
                        },
                    },
                ],
            },
        ],
    )
    content = response.choices[0].message.content
    return (content or "").strip()
