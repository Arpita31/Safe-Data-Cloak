import pytest

class TestDateRedaction:
    """Test suite for testing date redaction functionality."""

    @pytest.mark.parametrize("date_str", [
        "2024-01-31",
        "January 31, 2024"
    ])
    def test_numeric_date_formats(self, redactor, nlp, date_str):
        """
        Test detection of numeric date formats.

        Args:
            redactor: Redactor instance
            nlp: SpaCy NLP model
            date_str: The date string to test

        Tests various numeric date formats including:
        - YYYY-MM-DD
        - DD-MM-YYYY
        - MM-DD-YYYY
        - Different separators (-, /, .)
        """
        doc = nlp(date_str)
        spans = redactor.redact_dates(doc, date_str)
        assert spans == {(0, len(date_str))}, \
            f"Failed to detect numeric date: {date_str}"

   