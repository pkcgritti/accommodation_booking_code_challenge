from dataclasses import dataclass


@dataclass
class VoiceNoteStorageKey:
    booking_id: int
    voice_note_id: int

    def as_string(self) -> str:
        return f"booking{self.booking_id:08d}-voicenote{self.voice_note_id:08d}"
