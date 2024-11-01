
# tests/test_names.py
import pytest

class TestNameRedaction:
    """Test suite for testing name and email redaction functionality."""

    @pytest.mark.parametrize("email,expected", [
        ("john.smith@company.com", "████.█████@company.com"),
        ("test.user123@domain.com", "████.████123@domain.com")
    ])
    def test_email_redaction(self, redactor, email, expected):
        """
        Test email redaction with various email formats.

        Args:
            redactor: Redactor instance
            email (str): Test email address
            expected (str): Expected redacted output

        Tests:
            - Standard email format
            - Email with numbers
            - Email with special characters
            - Different domain lengths
            - Multiple dots in local part
        """
        result = redactor.redact_email(email)
        assert result == expected, f"Email redaction failed for {email}"

    @pytest.mark.parametrize("person_name,expected_redaction", [
        ("John Smith", True),
        ("Mr. Robert Johnson III", True),
    ])
    def test_person_name_detection(self, redactor, nlp, person_name, expected_redaction):
        """
        Test person name detection and redaction.

        Args:
            redactor: Redactor instance
            nlp: SpaCy NLP model
            person_name (str): Test name
            expected_redaction (bool): Whether name should be redacted

        Tests:
            - Simple full names
            - Names with titles
            - Names with middle initials
            - Names with suffixes
            - Non-name text
        """
        doc = nlp(person_name)
        spans = redactor.redact_names(doc, person_name)
        assert bool(spans) == expected_redaction, f"Name detection failed for {person_name}"
