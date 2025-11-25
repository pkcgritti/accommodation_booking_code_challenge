from logging import getLogger
from typing import final

import requests

from accommodation_booking.application.protocols.transcription_service import (
    TranscriptionResult,
    TranscriptionService,
)

logger = getLogger(__name__)


@final
class OpenAITranscriptionService(TranscriptionService):
    OPENAI_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"

    def __init__(self, api_key: str, model: str = "whisper-1", language: str = "en"):
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.payload = {"model": model, "language": language}

    def transcribe(
        self,
        audio_file: bytes,
        file_name: str,
        file_type: str,
    ) -> TranscriptionResult:
        logger.debug(
            "Transcribing %s using %s", file_type, "OpenAITranscriptionService"
        )

        response = requests.post(
            url=self.OPENAI_ENDPOINT,
            headers=self.headers,
            files={"file": (file_name, audio_file, file_type)},
            data=self.payload,
        )
        response.raise_for_status()

        json = response.json()
        return TranscriptionResult(transcript=json.get("text", ""))
