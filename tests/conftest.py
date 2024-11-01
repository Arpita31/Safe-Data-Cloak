import pytest
from pathlib import Path
import spacy
from redactor import Redactor

@pytest.fixture
def redactor():
    """Provide a Redactor instance for testing."""
    return Redactor()

@pytest.fixture
def nlp():
    """Provide a spaCy model for testing."""
    return spacy.load("en_core_web_trf")

@pytest.fixture
def sample_text():
    """Provide sample text containing various types of information."""
    return """
    John Smith lives at 123 Main St, Suite 100.
    Contact him at john.smith@example.com or +1 (123) 456-7890.
    Meeting scheduled for January 15, 2024.
    The wine tasting event is next week.
    """