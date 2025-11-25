from django.urls import path

from .views import (
    BookingDetailView,
    BookingListCreateView,
    VoiceNoteAudioDownloadView,
    VoiceNoteDetailView,
    VoiceNoteListCreateView,
)

urlpatterns = [
    path("", BookingListCreateView.as_view(), name="booking-list-create"),
    path("<int:pk>/", BookingDetailView.as_view(), name="booking-detail"),
    path(
        "<int:booking_id>/voice-notes/",
        VoiceNoteListCreateView.as_view(),
        name="voice-note-list-create",
    ),
    path(
        "<int:booking_id>/voice-notes/<int:pk>/",
        VoiceNoteDetailView.as_view(),
        name="voice-note-detail",
    ),
    path(
        "<int:booking_id>/voice-notes/<int:pk>/audio/",
        VoiceNoteAudioDownloadView.as_view(),
        name="voice-note-audio",
    ),
]
