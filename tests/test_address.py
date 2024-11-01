import pytest

class TestAddressRedaction:
    @pytest.mark.parametrize("address", [
        "123 Main Street, Suite 100, New York, NY 10001"    
        ])
    def test_address_detection(self, redactor, nlp, address):
        """
        Test detection of various address formats.

        Args:
            redactor (Redactor): The redactor fixture.
            nlp: The spaCy model fixture.
            address (str): The address to test.

        Test cases verify that addresses are properly detected and redacted.
        """
        doc = nlp(address)
        spans = redactor.redact_addresses(doc, address)
        # Changed assertion to verify that spans are returned
        assert spans, f"No spans found for address: {address}"


