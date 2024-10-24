import unittest
import spacy
import spacy.cli
import argparse
from transformers import pipeline
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Add parent directory to Python path
from Redactor import censor_text


class TestCensorText(unittest.TestCase):
    def setUp(self):
        spacy.cli.download("en_core_web_md")
        self.nlp = spacy.load("en_core_web_md")
        self.ner_pipeline = pipeline("ner")
    
    def test_censor_names(self):
        text = "John Doe lives in 123 Main St. He can be reached at +1-3527406574. He was born on 01/01/1994."
        entity_types = {
            'names': ['PERSON'],
            'dates': [],
            'phones': [],
            'address': [],
            'names_hf': ['I-PER'],
            'address_hf': ['']
        }
        args = argparse.Namespace(names=True, dates=False, phones=False, address=False, concept=[])
        CENSOR_CHAR = '█'

        censored_text = censor_text(text, entity_types, args, self.nlp, CENSOR_CHAR, self.ner_pipeline)

        # Assert that names are censored
        self.assertEqual(censored_text, "████████ lives in 123 Main St. He can be reached at +1-3527406574. He was born on 01/01/1994.")

    def test_censor_dates(self):
        text = "He was born on 01/01/1994 and started playing in NBA from December 12, 2005."
        entity_types = {
            'names': [],
            'dates': ['DATE', 'TIME'],
            'phones': [],
            'address': [],
            'names_hf': [],
            'address_hf': []
        }
        args = argparse.Namespace(names=False, dates=True, phones=False, address=False, concept=[])
        CENSOR_CHAR = '█'

        censored_text = censor_text(text, entity_types, args, self.nlp, CENSOR_CHAR, self.ner_pipeline)
        # Assert that dates are censored
        self.assertEqual(censored_text, "He was born on 01/01/1994 and started playing in NBA from █████████████████.")

    def test_censor_all(self):
        text = "John Doe lives in 123 Main St. He can be reached at +1-3527406574. He was born on 01/01/1994 in 12th St, Oregon. Trae Young was his neighbour in Downtown, Atlanata."
        entity_types = {
            'names': ['PERSON'],
            'dates': ['DATE', 'TIME'],
            'phones': ['CARDINAL'],
            'address': ['ORG', 'FAC', 'GPE'],
            'names_hf': ['I-PER'],
            'address_hf': ['I-LOC']
        }
        args = argparse.Namespace(names=True, dates=True, phones=True, address=True, concept=[])
        CENSOR_CHAR = '█'

        censored_text = censor_text(text, entity_types, args, self.nlp, CENSOR_CHAR, self.ner_pipeline)
        # Assert that names, dates, phones, and addresses are censored
        self.assertEqual(censored_text, "████████ lives in ███ ████ ██. He can be reached at +1-██████████. He was born on 01/01/1994 in ███████, ██████. ██████████ was his neighbour in ████████, ████████.")
    
    def test_censor_concept(self):
        text = "The patient has cancer and was treated with chemotherapy."
        entity_types = {
            'names': [],
            'dates': [],
            'phones': [],
            'address': [],
            'names_hf': [],
            'address_hf': []
        }
        args = argparse.Namespace(names=False, dates=False, phones=False, address=False, concept=['cancer', 'chemotherapy'])
        CENSOR_CHAR = '█'

        censored_text = censor_text(text, entity_types, args, self.nlp, CENSOR_CHAR, self.ner_pipeline)
        # Assert that concepts 'cancer' and 'chemotherapy' are censored
        self.assertEqual(censored_text, "█████████████████████████████████████████████████████████")

if __name__ == '__main__':
    unittest.main()
