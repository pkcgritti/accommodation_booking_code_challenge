from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from typing import cast

from accommodations.models import Accommodation
from bookings.models import Booking, VoiceNote


class BookingEndpointTests(APITestCase):

    def setUp(self) -> None:
        self._apartment = Accommodation.objects.create(
            name="Apartment",
            description="",
            price="100.0",
            location="City",
            type=Accommodation.AccommodationType.APARTMENT,
        )

        self._hotel = Accommodation.objects.create(
            name="Hotel",
            description="",
            price="100.0",
            location="City",
            type=Accommodation.AccommodationType.HOTEL,
        )

        Booking.objects.create(
            accommodation=self._apartment,
            start_date="2025-01-01",
            end_date="2025-01-08",
            guest_name="Guest 1",
        )

        Booking.objects.create(
            accommodation=self._hotel,
            start_date="2025-01-01",
            end_date="2025-01-08",
            guest_name="Guest 2",
        )

    def test_should_not_allow_booking(self):
        url = reverse("booking-list-create")

        cases = [
            (self._apartment.id, "2025-01-01", "2025-01-02"),
            (self._apartment.id, "2024-12-20", "2025-01-20"),
            (self._apartment.id, "2025-01-07", "2025-01-08"),
        ]
        for id, start_date, end_date in cases:
            payload = {
                "accommodation_id": id,
                "start_date": start_date,
                "end_date": end_date,
                "guest_name": "Guest 3",
            }

            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, 400)

    def test_should_allow_booking(self):
        url = reverse("booking-list-create")

        cases = [
            (self._hotel.id, "2025-01-01", "2025-01-02"),
            (self._hotel.id, "2024-12-30", "2025-01-20"),
            (
                self._apartment.id,
                "2025-01-08",
                "2025-01-10",
            ),  # should allow booking on previous end-date
        ]
        for id, start_date, end_date in cases:
            payload = {
                "accommodation_id": id,
                "start_date": start_date,
                "end_date": end_date,
                "guest_name": "Guest 3",
            }

            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, 201)


class VoiceNoteEndpointTests(APITestCase):
    def setUp(self) -> None:
        self.accommodation = Accommodation.objects.create(
            name="Apartment",
            description="",
            price="100.0",
            location="City",
            type=Accommodation.AccommodationType.APARTMENT,
        )
        self.booking = Booking.objects.create(
            accommodation=self.accommodation,
            start_date="2025-01-01",
            end_date="2025-01-08",
            guest_name="Guest",
        )

    @patch(
        "accommodation_booking.application.usecases.create_voice_note.transcribe_voice_note_command.delay"
    )
    @patch(
        "accommodation_booking.infrastructure.local.file_storage.LocalFileStorage.save_file_as"
    )
    def test_should_create_voice_note_and_enqueue_transcription(
        self, mock_save_file, mock_delay
    ):
        url = reverse("voice-note-list-create", kwargs={"booking_id": self.booking.id})
        audio = SimpleUploadedFile(
            "note.mp3", b"dummy-bytes", content_type="audio/mpeg"
        )

        response = self.client.post(url, {"audio_file": audio}, format="multipart")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(VoiceNote.objects.count(), 1)
        voice_note = cast(VoiceNote, VoiceNote.objects.first())
        self.assertEqual(voice_note.status, VoiceNote.Status.PENDING)
        self.assertEqual(voice_note.file_name, "note.mp3")
        self.assertEqual(voice_note.file_type, "audio/mpeg")
        mock_save_file.assert_called_once()
        mock_delay.assert_called_once_with(
            booking_id=self.booking.id,
            voice_note_id=voice_note.id,
            file_name="note.mp3",
            file_type="audio/mpeg",
        )

    @patch(
        "accommodation_booking.application.usecases.create_voice_note.transcribe_voice_note_command.delay"
    )
    @patch(
        "accommodation_booking.infrastructure.local.file_storage.LocalFileStorage.save_file_as"
    )
    def test_should_reject_invalid_mime(self, mock_save_file, mock_delay):
        url = reverse("voice-note-list-create", kwargs={"booking_id": self.booking.id})
        audio = SimpleUploadedFile(
            "note.txt", b"dummy-bytes", content_type="text/plain"
        )

        response = self.client.post(url, {"audio_file": audio}, format="multipart")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(VoiceNote.objects.count(), 0)
        mock_save_file.assert_not_called()
        mock_delay.assert_not_called()

    def test_should_require_audio_file(self):
        url = reverse("voice-note-list-create", kwargs={"booking_id": self.booking.id})
        response = self.client.post(url, {}, format="multipart")
        self.assertEqual(response.status_code, 400)
