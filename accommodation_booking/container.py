from dataclasses import dataclass
from pathlib import Path

from dependency_injector import containers, providers

from accommodation_booking.application.protocols.file_storage import FileStorage
from accommodation_booking.application.protocols.transcription_service import (
    TranscriptionService,
)
from accommodation_booking.application.usecases.create_voice_note import (
    CreateVoiceNoteUseCase,
)
from accommodation_booking.infrastructure.local.file_storage import LocalFileStorage
from accommodation_booking.infrastructure.local.transcription_service import (
    LocalTranscriptionService,
)
from accommodation_booking.infrastructure.openai.transcription_service import (
    OpenAITranscriptionService,
)

BOOKINGS_APP_DIRECTORY = Path(__file__).parent
CONFIG_FILE = BOOKINGS_APP_DIRECTORY / "config.yaml"


@dataclass
class UseCases:
    create_voice_note: CreateVoiceNoteUseCase


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_yaml(BOOKINGS_APP_DIRECTORY / "config.yaml")

    file_storage: providers.Provider[FileStorage] = providers.Factory(
        LocalFileStorage,
        data_directory=providers.Factory(Path, config.local_file_storage_directory),
    )

    transcription_service: providers.Provider[TranscriptionService] = (
        providers.Selector(
            config.transcription_provider,
            local=providers.Singleton(
                LocalTranscriptionService,
            ),
            openai=providers.Factory(
                OpenAITranscriptionService,
                api_key=config.openai.api_key,
                model=config.openai.model,
                language=config.openai.language,
            ),
        )
    )

    # UseCases
    create_voice_note_usecase: providers.Provider[CreateVoiceNoteUseCase] = (
        providers.Factory(
            CreateVoiceNoteUseCase,
            file_storage=file_storage,
        )
    )

    usecases: providers.Provider[UseCases] = providers.Factory(
        UseCases,
        create_voice_note=create_voice_note_usecase,
    )
