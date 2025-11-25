from unittest.mock import MagicMock, Mock, patch

from django.test import SimpleTestCase

from accommodation_booking.infrastructure.openai.transcription_service import (
    OpenAITranscriptionService,
)


class OpenAITranscriptionServiceTests(SimpleTestCase):
    def setUp(self):
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    @patch(
        "accommodation_booking.infrastructure.openai.transcription_service.requests.post"
    )
    def test_should_call_endpoint(self, mock_post: Mock):
        api_key = "test_api_key"
        service = OpenAITranscriptionService(api_key)

        fake_response = MagicMock()
        fake_response.json.return_value = {"text": "it should work"}
        fake_response.raise_for_status.return_value = None
        mock_post.return_value = fake_response

        fake_audio = b"fake data"
        fake_name = "some name"
        fake_type = "some type"
        result = service.transcribe(fake_audio, fake_name, fake_type)

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args

        self.assertEqual(result.transcript, "it should work")
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {api_key}")
