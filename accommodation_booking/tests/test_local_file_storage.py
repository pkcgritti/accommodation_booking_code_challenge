from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase

from accommodation_booking.infrastructure.local.file_storage import LocalFileStorage


class LocalFileStorageTests(SimpleTestCase):
    def setUp(self):
        self._tempdir = TemporaryDirectory()
        self._datadir = Path(self._tempdir.name) / "storage"
        self._storage = LocalFileStorage(self._datadir)
        self._storage.save_file_as(b"1234", "file")

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_save_file_as_should_work(self):
        self._storage.save_file_as(b"123456", "audiofile-user-2")
        file_path = self._datadir / "audiofile-user-2"
        self.assertTrue(file_path.exists())
        self.assertEqual(file_path.read_bytes(), b"123456")

    def test_load_file_should_return_without_errors(self):
        file = self._storage.load_file("file")
        self.assertEqual(file, b"1234")

    def test_load_file_should_raise_exception(self):
        with self.assertRaises(FileNotFoundError):
            self._storage.load_file("invalid_file_name")
