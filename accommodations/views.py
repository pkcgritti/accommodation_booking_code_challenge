from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics

from .models import Accommodation, AccommodationType
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
                enum=[t.value for t in AccommodationType],
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
