from django.test import SimpleTestCase

from accommodations.serializers import AccommodationSerializer


class AccommodationSerializerTests(SimpleTestCase):
    def test_requires_type(self):
        serializer = AccommodationSerializer(
            data={
                "name": "Test",
                "price": "100.0",
                "location": "City",
                "description": "",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("type", serializer.errors)

    def test_accepts_valid_type(self):
        serializer = AccommodationSerializer(
            data={
                "name": "Test",
                "price": 100.0,
                "location": "City",
                "description": "",
                "type": "hotel",
            }
        )
        self.assertTrue(serializer.is_valid())
