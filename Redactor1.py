import argparse
import glob
import os
import spacy
import sys
import warnings
import logging
import re
from collections import defaultdict
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet

# Download required NLTK data
nltk.download('punkt')
nltk.download('wordnet')

# Suppress TensorFlow, Keras, and Transformers warning logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings("ignore")
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('keras').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Define censor character
CENSOR_CHAR = '█'

# Define entity types for censoring
ENTITY_TYPES = {
    'names': ['PERSON'],
    'dates': ['DATE', 'TIME'],
    'phones': ['CARDINAL'],
    'address': ['ORG', 'FAC', 'GPE'],
    'names_hf': ['I-PER'],
    'address_hf': ['I-LOC']
}

# Global counters for statistics
censorName = 0
censorAddress = 0
censorPhone = 0
censorDate = 0

# Define regex patterns for specific email fields including new ones (X-Origin and X-FileName)
message_id_pattern = re.compile(r'Message-ID:\s*<([^>]+)>')
date_pattern = re.compile(r'Date:\s*(.*)')
from_pattern = re.compile(r'From:\s*([\w\.-]+@[\w\.-]+)')
to_pattern = re.compile(r'To:\s*([\w\.-]+@[\w\.-]+)')
subject_pattern = re.compile(r'Subject:\s*(.*)')
mime_version_pattern = re.compile(r'Mime-Version:\s*(\d+\.\d+)')
content_type_pattern = re.compile(r'Content-Type:\s*(.*)')
content_transfer_encoding_pattern = re.compile(r'Content-Transfer-Encoding:\s*(.*)')
x_header_pattern = re.compile(r'X-[\w-]+:\s*(.*)')
x_origin_pattern = re.compile(r'X-Origin:\s*([A-Za-z-]+)')
x_filename_pattern = re.compile(r'X-FileName:\s*([\w\.-]+)')
WEEKDAYS = {"tomorrow", "yesterday", "today","monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "night", "day"}
phone_pattern =re.compile(r'''
        (\+?\d{1,3}[\s.-]?)?
        \(?\d{2,4}\)?[\s.-]?
        \d{2,4}[\s.-]?
        \d{2,4}[\s.-]?
        \d{2,4}
    ''', re.VERBOSE)

# Load Hugging Face NER pipeline
ner_pipeline = pipeline("ner")

# Function to censor the text using regex, spaCy, and NER models
def censor_text(text, entity_types, args, CENSOR_CHAR, ner_pipeline):
    global censorName, censorAddress, censorPhone, censorDate

    censorName = 0
    censorAddress = 0
    censorPhone = 0
    censorDate = 0
    phone_pattern = re.compile(r'^(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$')
    censored_text = text
    
    # Apply regex-based censorship for specific fields
    censored_text = message_id_pattern.sub(lambda match: 'Message-ID: <' + CENSOR_CHAR * len(match.group(1)) + '>', censored_text)
    
    # Custom date patterns
    custom_date_patterns = [
    r'\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12][0-9]|3[01])[/-](?:\d{2}|\d{4})\b',  # MM/DD/YYYY or M/D/YY
    r'\b\d{4}[/-](?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12][0-9]|3[01])\b',             # YYYY-MM-DD or YYYY-M-D
    r'\b(?:0?[1-9]|[12][0-9]|3[01])(st|nd|rd|th)?[- ]?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[- ]?\d{2,4}\b',  # DD Month YYYY
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s(?:0?[1-9]|[12][0-9]|3[01])(st|nd|rd|th)?,\s\d{4}\b',     # Month DD, YYYY
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}\b',             # Month YYYY
    r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[,]?\s(?:0?[1-9]|[12][0-9]|3[01])\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}\b',  # Day, DD Month YYYY
    r'\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12][0-9]|3[01])[/-]\d{2}\b',             # MM/DD/YY or M/D/YY
    r'\b\d{4}s\b',                                                                 # Decades, e.g., "1990s"
]


    for pattern in custom_date_patterns:
        date_regex = re.compile(pattern)
        censored_text = date_regex.sub(lambda match: CENSOR_CHAR * len(match.group()), censored_text)

    # SpaCy NER for names, dates, phones, and addresses
    doc = nlp(censored_text)
    for ent in doc.ents:
        if ent.text.lower() in WEEKDAYS:
            continue  # Skip redacting weekdays
        if ent.label_ in entity_types['names'] and args.names:
            censored_text = censored_text[:ent.start_char] + CENSOR_CHAR * len(ent.text) + censored_text[ent.end_char:]
            censored_text = from_pattern.sub(lambda match: 'From: ' + CENSOR_CHAR * len(match.group(1)), censored_text)
            censored_text = to_pattern.sub(lambda match: 'To: ' + CENSOR_CHAR * len(match.group(1)), censored_text)
            censored_text = subject_pattern.sub(lambda match: 'Subject: ' + CENSOR_CHAR * len(match.group(1)), censored_text)
            censored_text = x_origin_pattern.sub(lambda match: 'X-Origin: ' + CENSOR_CHAR * len(match.group(1)), censored_text)
            censored_text = x_filename_pattern.sub(lambda match: 'X-FileName: ' + CENSOR_CHAR * len(match.group(1)), censored_text)
            censorName += 1
        elif ent.label_ in entity_types['dates'] and args.dates:
            censored_text = censored_text[:ent.start_char] + CENSOR_CHAR * len(ent.text) + censored_text[ent.end_char:]
            censorDate += 1
        elif ent.label_ in entity_types['phones'] and args.phones:
            censored_text = phone_pattern.sub(lambda match: CENSOR_CHAR * len(match.group()), censored_text)
            censorPhone += 1
        elif ent.label_ in entity_types['address'] and args.address:
            censored_text = censored_text[:ent.start_char] + CENSOR_CHAR * len(ent.text) + censored_text[ent.end_char:]
            censorAddress += 1

    # Hugging Face Check (for additional name/address redaction)
    entities_hf = ner_pipeline(censored_text)
    for ent in entities_hf:
        label = ent['entity'].upper()
        score = ent['score']
        if label in entity_types['names_hf'] and score > 0.6 and args.names:
            start = ent['start']
            end = ent['end']
            censored_text = censored_text[:start] + CENSOR_CHAR * (end - start) + censored_text[end:]
            censorName += 1

        if label in entity_types['address_hf'] and score > 0.6 and args.address:
            start = ent['start']
            end = ent['end']
            censored_text = censored_text[:start] + CENSOR_CHAR * (end - start) + censored_text[end:]
            censorAddress += 1

    # NLTK-based Concept Censoring
    if args.concept:
        sentences = sent_tokenize(censored_text)
        censored_sentences = []
        
        for sent in sentences:
            censor_flag = False
            words = set(word_tokenize(sent.lower()))  # Use a set for faster lookup
            for concept in args.concept:
                synonyms = set()
                for syn in wordnet.synsets(concept.lower()):
                    # Add all lemma names (synonyms) of the synset to the set
                    synonyms.update(syn.lemma_names())

                # Check for weekday names to avoid censoring them
                if concept.lower() in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                    continue

                if any(word in words for word in synonyms):
                    censor_flag = True
                    break

            if censor_flag:
                censored_sentences.append(CENSOR_CHAR * len(sent))
            else:
                censored_sentences.append(sent)

        censored_text = '\n'.join(censored_sentences)




    return censored_text

# Function to generate statistics about what was redacted.
def generate_statistics():
    global censorName, censorAddress, censorPhone, censorDate
    
    statistics = defaultdict(int)
    statistics["Names"] = censorName
    statistics["Address and Country"] = censorAddress
    statistics["Date"] = censorDate
    statistics["Phone Numbers or Important Numbers"] = censorPhone
    
    return statistics

# Parse command-line arguments to control what gets redacted.
def parse_arguments():
    parser = argparse.ArgumentParser(description="Text censoring tool")
    
    parser.add_argument("--input", nargs='+', help="Input file(s) pattern(s)")
    parser.add_argument("--output", help="Output directory for censored files")
    parser.add_argument("--stats", help="Statistics output file or stderr/stdout")
    parser.add_argument('--concept', action='append', help="Censored_Concept")
    
    parser.add_argument("--names", action="store_true", help="Censor names")
    parser.add_argument("--dates", action="store_true", help="Censor dates")
    parser.add_argument("--phones", action="store_true", help="Censor phone numbers")
    parser.add_argument("--address", action="store_true", help="Censor addresses")
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    if args.output and not os.path.exists(args.output):
        os.makedirs(args.output)

    censored_texts = []
    clearFile = True

    for input_pattern in args.input:
        for input_file in glob.glob(input_pattern):
            with open(input_file, 'r', encoding='utf-8') as file:
                text = file.read()
                censored_text = censor_text(text, ENTITY_TYPES, args, CENSOR_CHAR, ner_pipeline)
                censored_texts.append(censored_text)

                # Write censored text to output directory
                output_file = os.path.join(args.output, os.path.basename(input_file) + '.censored')
                with open(output_file, 'w', encoding='utf-8') as outfile:
                    outfile.write(censored_text)

                # Generate statistics
                statistics = generate_statistics()

                # Write statistics to file or stdout/stderr
                if args.stats:
                    if args.stats == 'stderr':
                        print("--- Censoring statistics for " + input_file + " ---")
                        for key, value in statistics.items():
                            print(f"{key}: {value}", file=sys.stderr)
                    elif args.stats == 'stdout':
                        print("--- Censoring statistics for " + input_file + " ---")
                        for key, value in statistics.items():
                            print(f"{key}: {value}")
                    else:
                        if clearFile:
                            clearFile = False
                            with open(args.stats, 'w', encoding='utf-8') as stats_file:
                                pass

                        with open(args.stats, 'a', encoding='utf-8') as stats_file:
                            stats_file.write("--- Censoring statistics for " + input_file + " ---\n")
                            for key, value in statistics.items():
                                stats_file.write(f"{key}: {value}\n")
                            stats_file.write("\n")

if __name__ == "__main__":
    main()
