from django.urls import reverse
from rest_framework.test import APITestCase

from accommodations.models import AccommodationType


class AccommodationEndpointTests(APITestCase):
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
