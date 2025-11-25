from django.db import models

from accommodations.models import Accommodation
from bookings.valueobjects import VoiceNoteStorageKey


class Booking(models.Model):
    """Booking model"""

    accommodation = models.ForeignKey(
        Accommodation,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    guest_name = models.CharField(max_length=255)

    class Meta:
        db_table = "booking"
        ordering = ["id"]

    def __str__(self):
        return f"{self.guest_name} - {self.accommodation.name} ({self.start_date} to {self.end_date})"


class VoiceNote(models.Model):
    """Voice note model"""

    class Status(models.TextChoices):
        PENDING = ("pending", "Pending")
        SUCCEEDED = ("succeeded", "Succeeded")
        FAILED = ("failed", "Failed")

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="voicenotes",
    )
    transcript = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    file_name = models.TextField(blank=True)
    file_type = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def storage_key(self) -> VoiceNoteStorageKey:
        return VoiceNoteStorageKey(self.booking.id, self.id)

    class Meta:
        db_table = "voicenote"
        ordering = ["id"]

    def __str__(self):
        return f"Voice note for {self.booking.guest_name} - {self.status}"
