import pytest

class TestPhoneRedaction:
    """Test suite for testing phone number redaction functionality."""

    @pytest.mark.parametrize("phone_number", [
        "123-456-7890",
        "123.456.7890",
        "1234567890",
        "1-123-456-7890",
    ])
    def test_us_phone_formats(self, redactor, phone_number):
        """
        Test US phone number format detection.

        Args:
            redactor: Redactor instance
            phone_number (str): Test phone number

        Tests:
            - Standard format (123-456-7890)
            - Dot format
            - No separator format
            - With country code
            - Different separator combinations
        """
        spans = redactor.redact_phones(phone_number)
        assert spans == {(0, len(phone_number))}, \
            f"Failed to detect US phone number: {phone_number}"
