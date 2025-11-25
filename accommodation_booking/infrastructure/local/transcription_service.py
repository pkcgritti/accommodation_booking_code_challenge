from io import BytesIO
from logging import getLogger
from typing import final

from faster_whisper import WhisperModel

from accommodation_booking.application.protocols.transcription_service import (
    TranscriptionResult,
    TranscriptionService,
)

logger = getLogger(__name__)


@final
class LocalTranscriptionService(TranscriptionService):
    def __init__(self):
        self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def transcribe(self, audio_file: bytes, _: str, file_type: str) -> TranscriptionResult:
        logger.debug("Transcribing %s using %s", file_type, "LocalTranscriptionService")
        segments, __ = self.model.transcribe(BytesIO(audio_file))
        return TranscriptionResult(transcript=" ".join([s.text for s in segments]))
