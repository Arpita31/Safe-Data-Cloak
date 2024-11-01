import pytest

class TestConceptRedaction:
    @pytest.mark.parametrize("text,concept,should_match", [
        ("A fine vineyard indeed.", "wine", True),
        ("Completely unrelated text.", "wine", False)
    ])
    def test_concept_matching(self, redactor, text, concept, should_match):
        """
        Test concept matching with exact and semantic matching.

        Args:
            redactor (Redactor): The redactor fixture.
            text (str): Input text to test.
            concept (str): Concept to search for.
            should_match (bool): Expected match result.
        """
        spans = redactor.redact_concepts(text, [concept])
        if should_match:
            assert spans, f"Expected to find concept '{concept}' in text: {text}"
        else:
            assert not spans, f"Unexpectedly found concept '{concept}' in text: {text}"