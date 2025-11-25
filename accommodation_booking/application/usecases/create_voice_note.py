from accommodation_booking.application.commands.transcribe_voice_note import (
    transcribe_voice_note_command,
)
from accommodation_booking.application.protocols.file_storage import FileStorage
from bookings.models import VoiceNote
from logging import getLogger

logger = getLogger(__name__)

ACCEPTED_AUDIO_MIME_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/mpga",
    "audio/mpeg3",
    "audio/mp4",
    "audio/aac",
    "audio/x-aac",
    "audio/wav",
    "audio/x-wav",
    "audio/flac",
    "audio/x-flac",
    "audio/ogg",
    "audio/opus",
    "audio/webm",
}


INTERCHANGEABLE_VIDEO_MIME_TYPES = {
    "video/mp4",
    "video/mpeg",
    "video/webm",
}

VIDEO_TO_AUDIO_MIME_MAP = {
    "video/mp4": "audio/mp4",
    "video/mpeg": "audio/mpeg",
    "video/webm": "audio/webm",
}


class CreateVoiceNoteUseCase:
    def __init__(
        self,
        file_storage: FileStorage,
    ):
        self.file_storage = file_storage

    def execute(
        self,
        booking_id: int,
        audio_file: bytes,
        file_name: str,
        file_type: str,
    ) -> VoiceNote:

        if (
            file_type not in ACCEPTED_AUDIO_MIME_TYPES
            and file_type not in INTERCHANGEABLE_VIDEO_MIME_TYPES
        ):
            raise ValueError(
                "Invalid file type. Must be supported audio or convertible video MIME type."
            )

        if file_type in INTERCHANGEABLE_VIDEO_MIME_TYPES:
            file_type = VIDEO_TO_AUDIO_MIME_MAP[file_type]

        voice_note = VoiceNote.objects.create(
            booking_id=booking_id,
            file_name=file_name,
            file_type=file_type,
        )

        self.file_storage.save_file_as(audio_file, voice_note.storage_key.as_string())
        logger.debug(
            "Sending Transcribe Voice Note Command to Celery Worker"
            + " (booking_id: %d, voice_note_id: %d, file_name: %s, file_type: %s",
            booking_id,
            voice_note.id,
            file_name,
            file_type,
        )
        transcribe_voice_note_command.delay(  # type: ignore
            booking_id=booking_id,
            voice_note_id=voice_note.id,
            file_name=file_name,
            file_type=file_type,
        )

        return voice_note
