from logging import getLogger

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import Response

from accommodation_booking.container import ApplicationContainer, UseCases

from .models import Booking, VoiceNote
from .serializers import BookingSerializer, VoiceNoteSerializer

logger = getLogger("django.request")


class BookingListCreateView(generics.ListCreateAPIView):
    """List all bookings or create a new booking"""

    queryset = Booking.objects.select_related("accommodation").all()
    serializer_class = BookingSerializer

    @extend_schema(
        summary="List all bookings",
        description="Get a list of all bookings",
        tags=["Bookings"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new booking",
        description="Create a new booking for an accommodation",
        tags=["Bookings"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a booking"""

    queryset = Booking.objects.select_related("accommodation").all()
    serializer_class = BookingSerializer

    @extend_schema(
        summary="Get booking by ID",
        description="Retrieve a specific booking by its ID",
        tags=["Bookings"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update booking",
        description="Update a specific booking",
        tags=["Bookings"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Delete booking",
        description="Delete a specific booking",
        tags=["Bookings"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update booking",
        description="Update specific fields of a booking",
        tags=["Bookings"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class VoiceNoteListCreateView(generics.ListCreateAPIView):
    """List all voice notes or create a new voice note"""

    parser_classes = [MultiPartParser]
    serializer_class = VoiceNoteSerializer

    def get_queryset(self):
        return VoiceNote.objects.filter(booking_id=self.kwargs["booking_id"])

    @extend_schema(
        summary="List all voice notes",
        description="Get a list of all voice notes associated with a booking",
        tags=["VoiceNotes"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new voice note",
        description="Create a new voice note for a booking",
        tags=["VoiceNotes"],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "audio_file": {
                        "type": "string",
                        "format": "binary",
                    }
                },
            }
        },
    )
    @inject
    def post(
        self,
        request,
        usecases: UseCases = Provide[ApplicationContainer.usecases],
        *args,
        **kwargs,
    ):
        audio_file_handle = request.FILES.get("audio_file")
        if not audio_file_handle:
            return Response({"audio_file": ["File required"]}, status=400)

        booking_id = kwargs["booking_id"]
        audio_file = audio_file_handle.read()
        file_name = audio_file_handle.name
        file_type = audio_file_handle.content_type

        try:
            voice_note = usecases.create_voice_note.execute(
                booking_id, audio_file, file_name, file_type
            )
        except Exception as ex:
            logger.exception(ex)
            return Response(
                {"message": "failed", "cause": str(ex)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = self.get_serializer(voice_note)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class VoiceNoteDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a voice note"""

    serializer_class = VoiceNoteSerializer

    def get_queryset(self):
        return VoiceNote.objects.filter(booking_id=self.kwargs["booking_id"])

    @extend_schema(
        summary="Get voice note by ID",
        description="Retrieve a specific voice note by its ID",
        tags=["VoiceNotes"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Delete voice note",
        description="Delete a specific voice note",
        tags=["VoiceNotes"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
