from django.urls import path

from .views import (
    AccommodationAvailabilityView,
    AccommodationDetailView,
    AccommodationListCreateView,
)

urlpatterns = [
    path("", AccommodationListCreateView.as_view(), name="accommodation-list-create"),
    path("<int:pk>/", AccommodationDetailView.as_view(), name="accommodation-detail"),
    path(
        "<int:pk>/availability/",
        AccommodationAvailabilityView.as_view(),
        name="accommodation-availability",
    ),
]
