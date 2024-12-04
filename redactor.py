import spacy
import re
from pathlib import Path
import argparse
import glob
import json
from typing import List, Set, Dict
import logging
import pyap
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import sys


class RedactionStats:
    def __init__(self):
        """
            Initialize RedactionStats
        """
        self.names_count = 0
        self.dates_count = 0
        self.phones_count = 0
        self.addresses_count = 0
        self.concepts: Dict[str, int] = {}
        self.files_processed = 0
        self.total_words_redacted = 0

    def to_dict(self) -> dict:
        """
            Convert the redaction statistics to a dictionary suitable for JSON output.
            Returns:
                dict: redaction statistics dictionary.
        """
        self.total_words_redacted = self.names_count + self.dates_count + self.phones_count + self.addresses_count + sum(self.concepts.values())
        return {
            "files_processed": self.files_processed,
            "total_words_redacted": self.total_words_redacted,
            "names_redacted": self.names_count,
            "dates_redacted": self.dates_count,
            "phones_redacted": self.phones_count,
            "addresses_redacted": self.addresses_count,
            "concepts_redacted": self.concepts
        }


class Redactor:
    def __init__(self):
        """
            Sets up the NLP model, compiles regex patterns, and initializes models for NER and sentence embeddings.
        """
        self.nlp = spacy.load("en_core_web_trf")
        self.stats = RedactionStats()

        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logging.error(f"Error loading sentence transformer: {str(e)}")
            self.sentence_model = None

        self.phone_pattern = re.compile(
            r'\b(\+?\d{1,3})?[-.\s]?\(?(\d{1,4})\)?[-.\s]?(\d{2,5})([-.\s]?\d{2,4}){1,4}\b'
        )
        self.date_pattern = re.compile(
            r'\b(?:(?:(\d{4})[-/.](\d{2})[-/.](\d{2}))|'                # Matches YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
            r'(?:(\d{2})[-/.](\d{2})[-/.](\d{4}))|'                      # Matches DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY
            r'(?:(\d{2})[-/.](\d{2})[-/.](\d{2}))|'                      # Matches MM-DD-YY, MM/DD/YY
            r'(?:(\d{4})年(\d{2})月(\d{2})日)|'                          # Matches YYYY年MM月DD日 (Japanese format)
            r'(?:(\d{2})[-/.](\d{2})[-/.](\d{4}))|'                      # Matches MM-DD-YYYY, MM/DD/YYYY, MM.DD.YYYY
            r'(?:(\d{1,2})(?:st|nd|rd|th)?\s'                            # Matches ordinal dates, e.g., "31st December 2024"
            r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|'
            r'Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s(\d{4}))|'
            r'(?:(\d{4})\s'                                              # Matches formats like "2024, December 31"
            r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|'
            r'Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s(\d{1,2}))|'
            r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|'
            r'Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s(\d{4}))\b'  # Matches "Dec 2024" or "December 2024"
        )
        self.address_patterns = [
            # Street addresses with numbers and common street types
            re.compile(
                r'\b\d+\s+[A-Za-z\s]+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|'
                r'Lane|Ln\.?|Drive|Dr\.?|Court|Ct\.?|Circle|Cir\.?|Trail|Trl\.?|Way|Place|Pl\.?|'
                r'Terrace|Ter\.?|Plaza|Highway|Hwy\.?|Parkway|Pkwy\.?)'
                r'(?:[,\s]+(?:Suite|Ste\.?|Floor|Fl\.?|Unit|Apt\.?|Apartment|Room|Rm\.?)?\s*'
                r'[#]?\d*[A-Za-z]?)?\s*[,\s]*(?:[A-Za-z\s]+[,\s]+[A-Z]{2}\s*\d{5}(?:-\d{4})?)?',
                re.IGNORECASE
            ),
            # PO Boxes
            re.compile(r'\b(?:P\.?\s*O\.?\s*Box|PO\s*Box)\s+\d+', re.IGNORECASE),
            # ZIP codes
            re.compile(r'\b[A-Z]{2}\s*\d{5}(?:-\d{4})?\b'),
            # Floor/Suite/Unit patterns
            re.compile(r'\b(?:Suite|Ste\.?|Floor|Fl\.?|Unit|Apt\.?|Apartment|Room|Rm\.?)\s*[#]?\d+[A-Za-z]?\b', re.IGNORECASE),
            # Building numbers with ordinal indicators
            re.compile(r'\b\d+(?:st|nd|rd|th)\s+(?:Floor|Fl\.?)', re.IGNORECASE)
        ]

        # Load Hugging Face NER model for additional entity recognition
        # self.tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        # self.ner_model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        # self.ner_pipeline = pipeline("ner", model=self.ner_model, tokenizer=self.tokenizer, aggregation_strategy="simple")

    def redact_text(self, text: str, redact_chars: str = '█') -> str:
        """
            Add redaction character
            Args:
                text: text for redaction
                redact_chars: Defaults to '█'.
            Returns:
                str: The redacted text.
        """
        return redact_chars * len(text)

    def redact_email(self, email: str) -> str:
        """
            Email redaction.
            Args:
                email: input email.
            Returns:
                str: redacted email
        """
        if '@' not in email:
            return email  # If it's not a valid email, return it unchanged

        local_part, domain = email.split('@', 1)
        # Redact each alphabetic character in the local part, while preserving numeric parts
        redacted_local = ''.join('█' if c.isalpha() else c for c in local_part)
        return f"{redacted_local}@{domain}"

    def redact_names(self, doc: spacy.tokens.Doc, text: str) -> Set[tuple]:
        """
            Find and mark names for redaction.
            Args:
                doc: The spaCy document containing the parsed text.
                texr: The original text.
            Returns:
                Set: A set of tuples representing the spans (start, end) of names to be redacted.
        """
        spans = set()
        redacted_text = text
        shift = 0

        # Redact person names identified by spaCy
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                redacted_name = '█' * (ent.end_char - ent.start_char)
                start, end = ent.start_char + shift, ent.end_char + shift
                redacted_text = redacted_text[:start] + redacted_name + redacted_text[end:]
                shift += len(redacted_name) - (ent.end_char - ent.start_char)
                spans.add((start, start + len(redacted_name)))
                self.stats.names_count += 1

        # Find and redact email addresses
        email_pattern = re.compile(r'\b([a-zA-Z0-9._\'-]+)@([\w.-]+\.[a-zA-Z]{2,})\b')
        for match in email_pattern.finditer(text):
            original_email = match.group()
            redacted_email = self.redact_email(original_email)
            start, end = match.start() + shift, match.end() + shift

            # Only add to spans and increment count if the email was actually redacted
            if original_email != redacted_email:
                redacted_text = redacted_text[:start] + redacted_email + redacted_text[end:]
                shift += len(redacted_email) - len(original_email)
                spans.add((start, start + len(redacted_email)))
                self.stats.names_count += 1

        return spans

    def redact_dates(self, doc: spacy.tokens.Doc, text: str) -> Set[tuple]:
        """
            Redact dates using regex and spaCy NER.
            Args:
                doc: The spaCy document containing the parsed text.
                text: The original text.
            Returns:
                Set: A set of tuples representing the spans (start, end) of dates to be redacted.
        """
        spans = set()

        # Redact dates identified by spaCy
        for ent in doc.ents:
            if ent.label_ == 'DATE':
                spans.add((ent.start_char, ent.end_char))
                self.stats.dates_count += 1

        # Redact dates using regex patterns
        for match in self.date_pattern.finditer(text):
            spans.add((match.start(), match.end()))
            self.stats.dates_count += 1

        return spans

    def redact_phones(self, text: str) -> Set[tuple]:
        """
            Redact phone numbers using regex.
            Args:
                text: The original text.
            Returns:
                Set: A set of tuples representing the spans (start, end) of phone numbers to be redacted.
        """
        spans = set()
        for match in self.phone_pattern.finditer(text):
            spans.add((match.start(), match.end()))
            self.stats.phones_count += 1
        return spans

    def redact_addresses(self, doc: spacy.tokens.Doc, text: str) -> Set[tuple]:
        """
            Find and mark addresses for redaction using enhanced patterns, spaCy NER, and pyap2.
            Args:
                doc: The spaCy document containing the parsed text.
                text: The original text.
            Returns:
                Set: A set of tuples representing the spans (start, end) of addresses to be redacted.
        """
        spans = set()

        # Use enhanced regex patterns for address detection
        for pattern in self.address_patterns:
            for match in pattern.finditer(text):
                # Get surrounding context
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]

                # If it looks like a complete address, add it
                if any(indicator in context.lower() for indicator in ['street', 'st', 'ave', 'road', 'floor', 'suite']):
                    spans.add((match.start(), match.end()))
                    self.stats.addresses_count += 1

        # Use spaCy NER to detect location-based entities
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC', 'FAC']:
                # Get surrounding context
                start = max(0, ent.start_char - 30)
                end = min(len(text), ent.end_char + 30)
                context = text[start:end]

                # If it appears to be part of an address, add it
                if any(pattern.search(context) for pattern in self.address_patterns):
                    spans.add((ent.start_char, ent.end_char))
                    self.stats.addresses_count += 1

        # Use pyap to detect addresses in the text
        for country in ('US', 'CA', 'GB'):  # Modify as needed for specific countries
            pyap_addresses = pyap.parse(text, country=country)
            for address in pyap_addresses:
                # Get the position of the address text within the full text
                start = text.find(address.full_address)
                end = start + len(address.full_address)
                if start != -1:  # Ensure address is found in the text
                    spans.add((start, end))
                    self.stats.addresses_count += 1

        return spans

    def redact_concepts(self, text: str, concepts: List[str]) -> Set[tuple]:
        """
            Redact entire lines containing specific concepts.
            Args:
                text: The original text.
                concepts: A list of concepts (keywords or phrases) to search for in the text.
            Returns:
                Set: A set of tuples representing the spans (start, end) of lines to be redacted.
        """

        spans = set()
        if not text.strip() or not concepts:
            return spans

        current_pos = 0
        for line in text.split('\n'):
            if line.strip():
                line_lower = line.lower()
                # Check exact matches first
                if any(concept.lower() in line_lower for concept in concepts):
                    matched_concept = next(c for c in concepts if c.lower() in line_lower)
                    self.stats.concepts[matched_concept] = self.stats.concepts.get(matched_concept, 0) + 1
                    spans.add((current_pos, current_pos + len(line)))
                # Try semantic matching if available and no exact match found
                elif self.sentence_model:
                    try:
                        similarities = cosine_similarity(
                            [self.sentence_model.encode(line_lower, convert_to_numpy=True)],
                            self.sentence_model.encode(concepts, convert_to_numpy=True)
                        )[0]
                        if max(similarities) > 0.45:
                            concept = concepts[np.argmax(similarities)]
                            self.stats.concepts[concept] = self.stats.concepts.get(concept, 0) + 1
                            spans.add((current_pos, current_pos + len(line)))
                    except Exception as e:
                        logging.warning(f"Error in semantic similarity calculation: {str(e)}")
            current_pos += len(line) + 1

        return spans

    def redact_document(self, input_path: str, flags: argparse.Namespace) -> str:
        """
            Process a single document and apply all requested redactions.
            Args:
                input_path: The path to the input file.
                flags: The parsed command-line arguments containing redaction options.
            Returns:
                str: The redacted text.
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()

        doc = self.nlp(text)
        spans_to_redact = set()

        if flags.names:
            spans_to_redact.update(self.redact_names(doc, text))

        if flags.dates:
            spans_to_redact.update(self.redact_dates(doc, text))

        if flags.phones:
            spans_to_redact.update(self.redact_phones(text))

        if flags.address:
            spans_to_redact.update(self.redact_addresses(doc, text))

        if flags.concept:
            spans_to_redact.update(self.redact_concepts(text, flags.concept))

        spans_to_redact = sorted(spans_to_redact)
        redacted_text = ''
        last_end = 0

        for start, end in spans_to_redact:
            if start < last_end:
                continue
            redacted_text += text[last_end:start]
            redacted_text += self.redact_text(text[start:end])
            last_end = end

        redacted_text += text[last_end:]
        self.stats.files_processed += 1

        return redacted_text


def setup_argparse() -> argparse.ArgumentParser:
    """
    Set up command line argument parsing with flexible argument combinations.
    Returns:
        argparse.ArgumentParser: The argument parser with configured options.
    """
    parser = argparse.ArgumentParser(description='Redact sensitive information from text files.')
    
    # Required argument
    parser.add_argument('--input', required=True, help='Input files glob pattern')
    
    # Optional redaction flags
    redaction_group = parser.add_argument_group('redaction options')
    redaction_group.add_argument('--names', action='store_true', help='Redact names')
    redaction_group.add_argument('--dates', action='store_true', help='Redact dates')
    redaction_group.add_argument('--phones', action='store_true', help='Redact phone numbers')
    redaction_group.add_argument('--address', action='store_true', help='Redact addresses')
    redaction_group.add_argument('--concept', action='append', help='Redact concepts (can be specified multiple times)')
    
    # Output options
    output_group = parser.add_argument_group('output options')
    output_group.add_argument('--output', default='files', 
                              help='Output directory (default: files)')
    output_group.add_argument('--stats', help='Statistics output file (optional, can be "stdout" or "stderr")')
    
    return parser

def validate_args(args: argparse.Namespace) -> bool:
    """
    Validate command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        bool: True if arguments are valid, False otherwise
    """
    # Check if at least one redaction option is specified
    redaction_options = [args.names, args.dates, args.phones, args.address]
    if not any(redaction_options) and not args.concept:
        logging.error("Error: At least one redaction option must be specified "
                     "(--names, --dates, --phones, --address, or --concept)")
        return False
    return True


def main():
    """
        Parses command-line arguments, processes input files, applies redactions, and outputs results.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Validate arguments
    if not validate_args(args):
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    redactor = Redactor()

    input_files = list(glob.glob(args.input))
    if not input_files:
        logging.error(f"No files found matching pattern: {args.input}")
        sys.exit(1)
    
    for input_path in input_files:
        try:
            redacted_text = redactor.redact_document(input_path, args)
            
            # Create output file
            input_file = Path(input_path)
            output_path = output_dir / f"{input_file.stem}.censored"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(redacted_text)
            
        except Exception as e:
            logging.error(f"Error processing {input_path}: {str(e)}")
            continue

    # Handle statistics output
    if args.stats:
        stats_dict = redactor.stats.to_dict()
        try:
            if args.stats == 'stderr':
                json.dump(stats_dict, sys.stderr, indent=2)
                sys.stderr.write('\n')  # Add newline
            elif args.stats == 'stdout':
                json.dump(stats_dict, sys.stdout, indent=2)
                sys.stdout.write('\n')  # Add newline
            else:
                with open(args.stats, 'w') as f:
                    json.dump(stats_dict, f, indent=2)
        except Exception as e:
            logging.error(f"Error writing statistics: {str(e)}")


if __name__ == "__main__":
    main()
