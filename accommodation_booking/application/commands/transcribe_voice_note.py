from celery import shared_task
from dependency_injector.wiring import Provide, inject

from accommodation_booking.application.protocols.file_storage import FileStorage
from accommodation_booking.application.protocols.transcription_service import (
    TranscriptionService,
)
from bookings.models import VoiceNote
from bookings.valueobjects import VoiceNoteStorageKey


@shared_task
@inject
def transcribe_voice_note_command(
    booking_id: int,
    voice_note_id: int,
    file_name: str,
    file_type: str,
    file_storage: FileStorage = Provide["file_storage"],
    transcription_service: TranscriptionService = Provide["transcription_service"],
):
    storage_key = VoiceNoteStorageKey(
        booking_id=booking_id, voice_note_id=voice_note_id
    )
    audio_file = file_storage.load_file(storage_key.as_string())

    try:
        result = transcription_service.transcribe(
            audio_file,
            file_name,
            file_type,
        )

        VoiceNote.objects.filter(id=voice_note_id).update(
            transcript=result.transcript,
            status=VoiceNote.Status.SUCCEEDED,
        )

    except Exception as ex:
        VoiceNote.objects.filter(id=voice_note_id).update(
            status=VoiceNote.Status.FAILED,
        )
