import pytest
from email_redactor import EmailNameRedactor

@pytest.fixture
def redactor():
    return EmailNameRedactor()

def test_simple_email_redaction(redactor):
    input_email = "jennifer.stewart@enron.com"
    expected = "████████.███████@enron.com"
    assert redactor.redact_name_in_email(input_email) == expected

def test_single_name_email(redactor):
    input_email = "brien@am.sony.com"
    expected = "█████@am.sony.com"
    assert redactor.redact_name_in_email(input_email) == expected

def test_underscore_separated_email(redactor):
    input_email = "George_Leon@spe.sony.com"
    expected = "███████████@spe.sony.com"
    assert redactor.redact_name_in_email(input_email) == expected

def test_complex_name_email(redactor):
    input_email = "Sean.O'Brien@am.sony.com"
    expected = "████.███████@am.sony.com"
    assert redactor.redact_name_in_email(input_email) == expected

def test_multiple_emails_in_text(redactor):
    input_text = """
    Contact emails:
    jennifer.stewart@enron.com
    brien@am.sony.com
    George_Leon@spe.sony.com
    """
    expected_count = 3
    redacted_text, count = redactor.redact_emails_in_text(input_text)
    assert count == expected_count
    assert "jennifer.stewart@enron.com" not in redacted_text
    assert "brien@am.sony.com" not in redacted_text
    assert "George_Leon@spe.sony.com" not in redacted_text

def test_custom_redaction_char():
    redactor = EmailNameRedactor(redaction_char='*')
    input_email = "jennifer.stewart@enron.com"
    expected = "********.*******@enron.com"
    assert redactor.redact_name_in_email(input_email) == expected

def test_invalid_email(redactor):
    input_email = "not.an.email"
    assert redactor.redact_name_in_email(input_email) == input_email

def test_empty_string(redactor):
    assert redactor.redact_name_in_email("") == ""