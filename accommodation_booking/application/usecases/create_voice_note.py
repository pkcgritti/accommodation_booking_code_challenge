from accommodation_booking.application.commands.transcribe_voice_note import (
    transcribe_voice_note_command,
)
from accommodation_booking.application.protocols.file_storage import FileStorage
from bookings.models import VoiceNote


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
        voice_note = VoiceNote.objects.create(
            booking_id=booking_id,
            file_name=file_name,
            file_type=file_type,
        )

        self.file_storage.save_file_as(audio_file, voice_note.storage_key.as_string())

        transcribe_voice_note_command.delay(  # type: ignore
            booking_id=booking_id,
            voice_note_id=voice_note.id,
            file_name=file_name,
            file_type=file_type,
        )

        return voice_note
