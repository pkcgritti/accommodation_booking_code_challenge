from dataclasses import dataclass
from typing import Protocol


@dataclass
class TranscriptionResult:
    transcript: str


class TranscriptionService(Protocol):
    def transcribe(
        self,
        audio_file: bytes,
        file_name: str,
        file_type: str,
    ) -> TranscriptionResult: ...
