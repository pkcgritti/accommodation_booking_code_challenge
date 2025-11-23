from django.urls import reverse
from rest_framework.test import APITestCase

from accommodations.models import Accommodation, AccommodationType
from bookings.models import Booking


class AccommodationEndpointTests(APITestCase):
    def setUp(self):
        self._apartment = Accommodation.objects.create(
            name="Acc 1",
            description="",
            price="200.0",
            location="City",
            type="apartment",
        )
        self._hotel = Accommodation.objects.create(
            name="Acc 2",
            description="",
            price="100.0",
            location="City",
            type="hotel",
        )

        Booking.objects.create(
            accommodation=self._apartment,
            start_date="2025-01-01",
            end_date="2025-01-08",
            guest_name="Guest 1",
        )

        Booking.objects.create(
            accommodation=self._apartment,
            start_date="2025-01-08",
            end_date="2025-01-10",
            guest_name="Guest 2",
        )

        Booking.objects.create(
            accommodation=self._apartment,
            start_date="2025-01-12",
            end_date="2025-01-15",
            guest_name="Guest 3",
        )

        Booking.objects.create(
            accommodation=self._hotel,
            start_date="2025-01-01",
            end_date="2025-01-02",
            guest_name="Guest 4",
        )

    def test_list_accommodations(self):
        url = reverse("accommodation-list-create")

        response = self.client.get(url, data={"type": "apartment"})
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(url, data={"type": "hotel"})
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(url)
        self.assertEqual(response.data["count"], 2)

    def test_create_requires_type(self):
        url = reverse("accommodation-list-create")
        payload = {
            "name": "Test",
            "price": "100.00",
            "location": "City",
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("type", response.data)  # type: ignore

    def test_create_with_type(self):
        url = reverse("accommodation-list-create")
        payload = {
            "name": "Test",
            "price": "100.00",
            "location": "City",
            "type": "apartment",
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["type"], AccommodationType.APARTMENT)  # type: ignore

    def test_availability(self):
        cases = [
            (self._apartment, "2025-01-01", "2025-01-10"),
            (self._apartment, "2025-01-12", "2025-01-15"),
            (self._apartment, "2025-01-20", "2025-01-20"),
            (self._hotel, "2025-01-01", "2025-01-01"),
        ]

        for accommodation, reference_date, expected_date in cases:
            url = reverse("accommodation-availability", args=[accommodation.id])
            response = self.client.get(url, data={"date": reference_date})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.get("next_available_date"), expected_date)
