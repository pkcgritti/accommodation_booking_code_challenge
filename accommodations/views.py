from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, serializers
from rest_framework.response import Response

from bookings.models import Booking

from .models import Accommodation
from .serializers import AccommodationSerializer


class AccommodationListCreateView(generics.ListCreateAPIView):
    """List all accommodations or create a new accommodation"""

    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer

    @extend_schema(
        summary="List all accommodations",
        description="Get a list of all accommodations",
        parameters=[
            OpenApiParameter(
                name="type",
                description="Filter by accommodation type",
                required=False,
                type=OpenApiTypes.STR,
                enum=[t.value for t in Accommodation.AccommodationType],
            )
        ],
        tags=["Accommodations"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new accommodation",
        description="Create a new accommodation",
        tags=["Accommodations"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        accommodation_type = self.request.query_params.get("type")
        if accommodation_type:
            queryset = queryset.filter(type=accommodation_type.lower())
        return queryset


class AccommodationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an accommodation"""

    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer

    @extend_schema(
        summary="Get accommodation by ID",
        description="Retrieve a specific accommodation by its ID",
        tags=["Accommodations"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update accommodation",
        description="Update a specific accommodation",
        tags=["Accommodations"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Delete accommodation",
        description="Delete a specific accommodation",
        tags=["Accommodations"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update accommodation",
        description="Update specific fields of an accommodation",
        tags=["Accommodations"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class AccommodationAvailabilityView(generics.GenericAPIView):
    """Check if an accommodation is available at a given date"""

    queryset = Accommodation.objects.all()

    class RequestSerializer(serializers.Serializer):
        """Serializer to validate query input parameter"""

        date = serializers.DateField()

    class AvailabilityResponse(serializers.Serializer):
        """Serializer for availability response"""

        accommodation_id = serializers.IntegerField()
        next_available_date = serializers.DateField()

    @extend_schema(
        summary="Get next available date",
        description="Given a reference date, returns the next available date for the accommodation",
        tags=["Accommodations"],
        parameters=[
            OpenApiParameter(
                name="date",
                description="Reference date (YYYY-MM-DD)",
                required=True,
                type=OpenApiTypes.DATE,
            ),
        ],
        responses={
            200: AvailabilityResponse,
        },
    )
    def get(self, request, *args, **kwargs):
        accommodation = self.get_object()

        request_serializer = self.RequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        if accommodation.type != Accommodation.AccommodationType.APARTMENT:
            serializer = self.AvailabilityResponse(
                {
                    "accommodation_id": accommodation.id,
                    "next_available_date": request_serializer.data.get("date"),
                }
            )
            return Response(serializer.data)

        queryset = Booking.objects.filter(
            accommodation_id=accommodation.id,
            end_date__gte=request_serializer.data.get("date"),
        ).order_by("start_date")

        next_available_date = (request_serializer.validated_data or {}).get("date")
        for booking in queryset:
            if (
                next_available_date < booking.start_date
                or next_available_date >= booking.end_date
            ):
                break
            next_available_date = booking.end_date

        serializer = self.AvailabilityResponse(
            {
                "accommodation_id": accommodation.id,
                "next_available_date": next_available_date,
            }
        )

        return Response(serializer.data)
