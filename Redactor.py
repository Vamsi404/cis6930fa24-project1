import argparse
import glob
import os
import spacy
from spacy.matcher import Matcher
import spacy.cli
import sys
import warnings
warnings.filterwarnings("ignore")
import logging
import re
from collections import defaultdict
from transformers import pipeline

# Suppress TensorFlow, Keras, and Transformers warning logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings("ignore")
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('keras').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)

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

#------SPACY------------------
spacy.cli.download("en_core_web_md")
nlp = spacy.load("en_core_web_md")

# #------Hugging Face------------
ner_pipeline = pipeline("ner")

# Add custom pattern to match dates in "mm/dd/yyyy" format
matcher = Matcher(nlp.vocab)
pattern = [{"SHAPE": "dd"}, {"ORTH": "/"}, {"SHAPE": "dd"}, {"ORTH": "/"}, {"SHAPE": "dddd"}]
matcher.add("DATE_FORMAT", [pattern])

# Define custom component to merge detected dates into a single token
@spacy.Language.component("merge_date_tokens")
def merge_date_tokens(doc):
    with doc.retokenize() as retokenizer:
        for match_id, start, end in matcher(doc):
            match_span = doc[start:end]
            retokenizer.merge(match_span)
    return doc

nlp.add_pipe("merge_date_tokens", after="ner")

# Function to censor the text
def censor_text(text, entity_types, args, nlp, CENSOR_CHAR, ner_pipeline):
    global censorName, censorAddress, censorPhone, censorDate
    censorName = 0
    censorAddress = 0
    censorPhone = 0
    censorDate = 0
    
    phone_pattern = re.compile(r'^(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$')
    censored_text = text
    doc_spacy = nlp(censored_text)

    # Spacy entity checks
    for ent in doc_spacy.ents:
        if ent.label_ in entity_types['names'] and args.names:
            start = ent.start_char
            end = ent.end_char
            censored_text = censored_text[:start] + CENSOR_CHAR * (end - start) + censored_text[end:]
            censorName += 1
        
        if ent.label_ in entity_types['dates'] and args.dates:
            start = ent.start_char
            end = ent.end_char
            censored_text = censored_text[:start] + CENSOR_CHAR * (end - start) + censored_text[end:]
            censorDate += 1
        
        if ent.label_ in entity_types['address'] and args.address:
            start = ent.start_char
            end = ent.end_char
            censored_text = censored_text[:start] + CENSOR_CHAR * (end - start) + censored_text[end:]
            censorAddress += 1

        if ent.label_ in entity_types['phones'] and args.phones:
            start = ent.start_char
            end = ent.end_char
            censored_text = censored_text[:start] + CENSOR_CHAR * (end - start) + censored_text[end:]
            censorPhone += 1
    if args.concept:
        for sent in doc_spacy.sents:
            for concept in args.concept:
                # Check if the concept or its synonyms appear in the sentence
                if concept in sent.text.lower():
                    start = sent.start_char
                    end = sent.end_char
                    censored_text = censored_text[:start] + CENSOR_CHAR * (end - start) + censored_text[end:]
                    break 

    # Regex for phone numbers
    for token in doc_spacy:
        if phone_pattern.search(token.text) and args.phones:
            start = token.idx
            end = start + len(token.text)
            censored_text = censored_text[:start] + CENSOR_CHAR * len(token.text) + censored_text[end:]
            censorPhone += 1

    # Hugging Face Check
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

    return censored_text

# Function to generate statistics
def generate_statistics():
    global censorName, censorAddress, censorPhone, censorDate
    statistics = defaultdict(int)
    statistics["Names"] = censorName
    statistics["Address and Country"] = censorAddress
    statistics["Date"] = censorDate
    statistics["Phone Numbers or Important Numbers"] = censorPhone
    return statistics

# Parse command-line arguments
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

# Main function to handle the process
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
                censored_text = censor_text(text, ENTITY_TYPES, args, nlp, CENSOR_CHAR, ner_pipeline)
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
