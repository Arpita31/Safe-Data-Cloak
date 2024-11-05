# cis6930fa24 -- Project 1 

Name: Arpita Patnaik

# Project Description 
Find the detailed project description on(https://ufdatastudio.com/cis6930fa24/assignments/project1).
<br /> Get a glob of files of specified input file type. <br /> Redact names, dates, phones and the specified concept from user.<br /> Save the file in 'file/' path with filename as <filename>.censored.

# How to install
```
    $ pipenv run pip install -U spacy
    $ pipenv run python -m pip install numpy==1.26
    $ pipenv run python -m spacy download en_core_web_trf
    $ pipenv install transformers
    $ pipenv run  pip install pyap
    $ pipenv install scikit-learn
    $ pipenv install sentence-transformers transformers
    $ pipenv install -e . 
```


## How to run
To tun the code:
```
   $ pipenv run python redactor.py --input '*.txt' \
                    --names --dates --phones --address\
                    --concept 'wine' \
                    --output 'files/' \
                    --stats stderr
```

To run the tests:
```
    $ pipenv run python -m pytest
```

Sample output stats:
```
    "files_processed": 1,
    "total_words_redacted": 0,
    "names_redacted": 30,
    "dates_redacted": 21,
    "phones_redacted": 36,
    "addresses_redacted": 11,
    "concepts_redacted": {
        "Wine": 4
    }
```
The stats were printed on terminal or if --stats <filename> is specified, it stores the stats file on the main directory.
                    
![video](video)
- Runs redactor.py within pipenv to redact data from all .txt files in the current directory.
- Applies specific redactions for names, dates, phone numbers, and addresses based on given flags.
- Uses the --concept 'kids' flag to redact any text related to the concept of "kids."
- Saves redacted files with a .censored extension in the files/ directory.
- Outputs redaction statistics to stderr for review and analysis.


## Functions 
1. Redactor.__init__(): Sets up the Spacy NLP model, initializes a sentence-transformers model for concept redaction, and compiles regex patterns for phone numbers, dates, and addresses. 
2. Redactor.redact_text(): Replace text with specified redaction characters('█').
3. Redactor.redact_email() - Redacts the an email address, replacing with alphabetic characters ('█').
4. Redactor.redact_names() - Identifies and redacts names in text using Spacy's NER model and regex to find names and email addresses, updating spans for redaction.
5. Redactor.redact_dates()- Detects and redacts dates using both Spacy NER and regex patterns, adding redaction spans and updating date redaction statistics.
6. Redactor.redact_phones() - Redacts phone numbers by matching regex patterns in the text and adding their spans to be censored.
7. Redactor.redact_addresses() - Finds and redacts addresses by using Spacy NER, regex patterns, and Pyap for location-based entities and address patterns.
8. Redactor.redact_concepts() - Searches for specified concepts in text to redact lines containing them, using sentence-transformers for semantic matching where exact matches fail.
9. Redactor.redact_document() - Processes an input file, applying all requested redactions to detected spans and returning the fully redacted text.
10. Redactor.setup_argparse() - Configures the command-line arguments for the script, enabling options for different types of redactions and file processing settings.
11. Redactor.main() - Parses command-line arguments, initiates the redaction process for each input file, outputs the redacted text to a specified directory, and optionally writes redaction statistics in JSON format.
12. RedactionStats.__init__(): Initializes counters for redacted items like names, dates, and total words redacted, providing a structure to track redaction statistics.
13. RedactionStats.to_dict(): Converts the statistics into a dictionary format for easy JSON output.

    

## Bugs and Assumptions

### Bugs:

1. name redaction for emails
<br />
input = 24139656.1075858626713.JavaMail.evans@thyme
<br />
expected output = 24139656.1075858626713.JavaMail.evans@thyme
<br />
actual output =  ██████████████████████.JavaMail.evans@thyme
<br />Explanation - to support phone redaction we have used numbers regEx which redacts the above case.

2. In phone redaction numbers except "+" sign are redacted. 

3. In Phone redaction short phone numbers are also getting redacted like "123 456 789"

4. Some addresses doesn't redact like  "123 Main Rd", "123 Main Blvd" and "123 Main Boulevard".

5. In date dedaction we are not checking the validity of the date. For instance, 13/13/2020 is also redacted.


### Assumptions:

1. In name redaction for emails
input = Sean.O'Brien@am.sony.com
<br />
expected output = ████████████████████████

2. In name redaction we redact the space between the first and last name as well.

3. In date redaction, we check for YYYY/MM/DD, DD-MM-YYYY, MM/DD/YY, 31st December 2024, 2024, December 31 or Dec 2024, etc.

4. In date dedaction we are not checking the validity of the date.

5. Stats we are showing how many number of changes happened under each category like names, dates, phones, addresses and concepts.

