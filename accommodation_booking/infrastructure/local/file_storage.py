import os
from pathlib import Path
from typing import final

from accommodation_booking.application.protocols.file_storage import FileStorage


@final
class LocalFileStorage(FileStorage):
    def __init__(self, data_directory: Path):
        self.data_directory = data_directory

    def save_file_as(self, file: bytes, file_id: str):
        if not self.data_directory.exists():
            os.makedirs(self.data_directory)

        file_path = self.get_file_path(file_id)
        with open(file_path, "wb") as fout:
            fout.write(file)

    def load_file(self, file_id: str) -> bytes:
        file_path = self.get_file_path(file_id)
        if file_path.exists():
            return file_path.read_bytes()
        raise FileNotFoundError(file_id)

    def get_file_path(self, file_id: str) -> Path:
        return self.data_directory / file_id
