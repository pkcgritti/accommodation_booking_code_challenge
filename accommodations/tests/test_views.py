from django.urls import reverse
from rest_framework.test import APITestCase

from accommodations.models import Accommodation, AccommodationType


class AccommodationEndpointTests(APITestCase):
    def setUp(self):
        Accommodation.objects.create(
            name="Acc 1",
            description="",
            price="200.0",
            location="City",
            type="apartment",
        )
        Accommodation.objects.create(
            name="Acc 2",
            description="",
            price="100.0",
            location="City",
            type="hotel",
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




