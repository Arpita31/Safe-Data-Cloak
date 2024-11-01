# cis6930fa24 -- Project 1 

Name: Arpita Patnaik

# Project Description 
Find the detailed project description on(https://ufdatastudio.com/cis6930fa24/assignments/project1).
Get a glob of files of specified input type. redact names, dates, phones and the specified concept from user. Save the file in 'file/' path with filename as <filename>.censored.

# How to install
pipenv run pip install -U spacy
<br />
pipenv run python -m pip install numpy==1.26
<br />
pipenv run python -m spacy download en_core_web_trf
<br />
pipenv install transformers
<br />
pipenv run  pip install pyap
<br />
pipenv install scikit-learn
<br />
pipenv install sentence-transformers transformers torch




## How to run
pipenv run python redactor.py --input '*.txt' \
                    --names --dates --phones --address\
                    --concept 'wine' \
                    --output 'files/' \
                    --stats stderr
                    
![video](video)


## Functions -- 
1. redact_text() - Replace text with specified redaction characters('█').
2. redact_email() - Redact the email.
3. redact_names() - Identify and redact names and emails from the text.
4. redact_dates()- Identify and redact date entities in the text using spaCy and regex.
5. redact_phones() - Identify and redact phone numbers using regex patterns.
6. redact_addresses() - Identify and redact addresses using spaCy, regex, and pyap.
7. redact_concepts() - Identify and redact entire lines containing specific concepts using semantic similarity.
8. redact_document() - Process a document to apply redactions based on specified flags.
9. setup_argparse() - Set up and return command-line argument parser for redaction options.
10. main() - """Parse arguments, process files, apply redactions, and save results."""

    

## Bugs and Assumptions

### Bugs:

1.name -> Email redaction
input = 24139656.1075858626713.JavaMail.evans@thyme
expected output = 24139656.1075858626713.JavaMail.evans@thyme
actual output =  ██████████████████████.JavaMail.evans@thyme

Explanation - to support phone redaction we have used numbers regEx which redacts the above case.


### Assumptions:

1. In name redaction for emails
input = Sean.O'Brien@am.sony.com
expected output = ████████████████████████

2. In name redaction we redact the space between the first and last name as well.

3. In date redaction, we check for YYYY<-,/,.>MM<-,/,.>DD, DD<-,/,.>MM<-,/,.>YYYY, MM</,->DD</,->YY, 31st December 2024, 2024, December 31 or Dec 2024.

4. In phone redaction numbers except + sign are redacted. 

5. In date dedaction we are not checking the validity of the date.

6. Stats we are showing how many number of changes happened under each category like names, dates, phones, addresses and concepts.
