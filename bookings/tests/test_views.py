from django.urls import reverse
from rest_framework.test import APITestCase

from accommodations.models import Accommodation, AccommodationType
from bookings.models import Booking


class BookingEndpointTests(APITestCase):

    def setUp(self) -> None:
        self._apartment = Accommodation.objects.create(
            name="Apartment",
            description="",
            price="100.0",
            location="City",
            type=AccommodationType.APARTMENT,
        )

        self._hotel = Accommodation.objects.create(
            name="Hotel",
            description="",
            price="100.0",
            location="City",
            type=AccommodationType.HOTEL,
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
            (self._apartment.id, "2025-01-08", "2025-01-10"), # should allow booking on previous end-date
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




