## Author: Vamsi Manda
## UFID: 43226231

## Overview

This tool is designed to censor specific types of sensitive information from text files, such as names, addresses, dates, phone numbers, and user-defined concepts. The program uses both **SpaCy** and **Hugging Face** transformers to detect named entities. It replaces detected entities with a censor character of choice (default: `█`), including censoring entire phrases and concepts.

## Key Features

- **Censor Types**: Supports censoring of names, dates, phone numbers, and addresses. It also supports censoring user-defined "concepts," which can be words or phrases that represent ideas, themes, or sensitive information.
- **Flexible Censorship**: You can choose which entities to censor and define custom concepts for censoring.
- **Statistics**: Outputs a summary of censored terms and types for each input file.
- **Customizable Censor Character**: The character used to replace sensitive terms can be customized (default is the block character `█`).
  
## Parameters and Flags

### Flags:
- `--input <pattern>`: One or more input files (e.g., `--input *.txt`).
- `--output <directory>`: Output directory to save the censored files.
- `--stats <file/stderr/stdout>`: Generates statistics about the censoring process and writes to a file or standard output.
- `--concept <word/phrase>`: User-defined concept to censor. This flag can be repeated for multiple concepts.
- `--names`: Censors names (detected by entity types `PERSON` or `I-PER`).
- `--dates`: Censors dates and times.
- `--phones`: Censors phone numbers and other cardinal values.
- `--address`: Censors addresses and geographical locations.
  
### Concept Flag:
The `--concept` flag allows censoring of entire sentences or paragraphs containing a specified word or phrase. For example, if the concept is "prison," it will also censor related terms like "jail" or "incarcerated." This is achieved through sentence-level censoring in SpaCy and Hugging Face.

The definition of a **concept** includes words or phrases that convey an idea or theme. For instance, if a sensitive concept like "confidential project" is provided, the program will censor any sentence containing the phrase "confidential project."

### Censoring Whitespace:
If censoring first and last names (e.g., "John Doe"), censoring whitespaces between the names would help obscure identity more effectively. This method is implemented for entities that represent full names.

## Examples of Usage

### Basic Censoring Example:
```bash
pipenv run python redactor.py --input '*.txt' --names --dates --phones --address --output 'docs/' --stats stdout
```
This command censors names and dates from the input file `input.txt` and saves the result to the `docs/` directory.

### Concept Censoring Example:
```bash
pipenv run python redactor.py --input '*.txt' --names --dates --phones --address--concept 'kids' --output 'docs/' --stats stdout
```
This command censors sentences related to kids from the input file and outputs statistics to the console.

### Statistics Output Example:
```bash
pipenv run python redactor.py --input '*.txt' --names --dates --phones --address--concept 'kids' --output 'docs/' --stats stats.txt
```
This command will generate a statistics summary file (`stats.txt`) showing the number of censored terms.

## Installation

To install and run the program, follow these steps:

1. Install the required Python packages using pipenv:
   ```bash
   pipenv install
   ```
2. Download necessary SpaCy models:
   ```bash
   pipenv run python -m spacy download en_core_web_md
   ```

## Tests & Running the Tests

# Tests for `censor_text` and `generate_statistics`

This module includes unit tests for both the `censor_text` function and the `generate_statistics` function, which are designed to censor sensitive information in text and generate relevant statistics about the text, respectively. The tests utilize the `unittest` framework and cover various scenarios to ensure both functions behave as expected.

### Test Cases

1. **Test Censor Names**
   - **Purpose**: Verifies that all names identified as PERSON entities are correctly censored in the text.
   - **Code**:
     ```python
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
     ```
   - **Expected Output**: The name "John Doe" is replaced with "████████".

2. **Test Censor Dates**
   - **Purpose**: Ensures that different date formats, including specific patterns and common formats, are accurately censored.
   - **Code**:
     ```python
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
     ```
   - **Expected Output**: The date "December 12, 2005" is replaced with "████████████████".

3. **Test Censor All**
   - **Purpose**: Confirms that all specified entities (names, dates, phone numbers, and addresses) are censored correctly in a complex sentence.
   - **Code**:
     ```python
     def test_censor_all(self):
         text = "John Doe lives in 123 Main St. He can be reached at +1-3527406574. He was born on 01/01/1994 in 12th St, Oregon. Trae Young was his neighbour in Downtown, Atlanta."
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
     ```
   - **Expected Output**: All sensitive information (names, dates, phone numbers, and addresses) is censored.

4. **Test Concept Censoring**
   - **Purpose**: Checks the ability to censor specific concepts or terms defined by the user.
   - **Code**:
     ```python
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
         self.assertEqual(censored_text, "█████████████████████████████████████████████████████████.")
     ```
   - **Expected Output**: The concepts "cancer" and "chemotherapy" are replaced with "█".

5. **Test File Existence**
   - **Purpose**: Confirms that the necessary Python files for the project exist in the specified directory.
   - **Code**:
     ```python
     class TestFileExistence(unittest.TestCase):

         def test_censoror_file_exists(self):
             file_path = './Redactor.py'
             self.assertTrue(os.path.exists(file_path), f"File '{file_path}' does not exist.")

         def test_main_file_exists(self):
             # Use an absolute path
             file_path = os.path.abspath('./Redactor.py')
             self.assertTrue(os.path.exists(file_path), f"File '{file_path}' does not exist.")
     ```
   - **Expected Output**: Validates the existence of the `Redactor.py` file, ensuring the necessary components are present for the application to run.

6. **Test Generate Statistics**
   - **Purpose**: Validates that the `generate_statistics` function produces non-negative statistics for the specified categories.
   - **Code**:
     ```python
     class TestGenerateStatistics(unittest.TestCase):
    
         def test_generate_statistics(self):
             # Initial values test
             statistics = generate_statistics()

             # Assert that statistics are generated correctly
             self.assertTrue(statistics["Names"] >= 0)
             self.assertTrue(statistics["Address and Country"] >= 0)
             self.assertTrue(statistics["Date"] >= 0)
             self.assertTrue(statistics["Phone Numbers or Important Numbers"] >= 0)
     ```
   - **Expected Output**: All statistics should be non-negative integers, indicating successful generation.

### Explanation of the Code

The test code is structured using Python's `unittest` framework. It includes the following components:

- **Imports**: Essential libraries such as `unittest` and `os` are imported to facilitate testing and file system interactions.
- **Test Classes**: Classes named `TestFileExistence` and `TestGenerateStatistics` inherit from `unittest.TestCase` and contain methods for testing file existence and statistics generation, respectively.
- **Test Methods**: Each test method checks specific functionalities, such as the existence of the `Redactor.py` file and the correctness of statistics generated by the `generate_statistics` function.
- **Main Block**: The test suite is executed when the script runs as the main module.

This structured approach ensures that each aspect of the `censor_text` and `generate_statistics` functions, as well as the project's file structure, is tested thoroughly, enabling confidence in their reliability and accuracy.

Ensure all tests are written for each feature and can be executed with the following command:
```bash
pipenv run python -m pytest
```

## Stats Output Format

The stats will include the type and count of censored terms for each file processed. Example output:
```
--- Censoring statistics for input.txt ---
Names: 3
Address and Country: 2
Date: 4
Phone Numbers or Important Numbers: 1
```

## Known Bugs

- **Whitespace Censoring**: In cases where entire names (e.g., "John Doe") are censored, the spaces between words may not always be properly handled when using complex sentence structures.
- **Accuracy in Concept Matching**: While concepts can capture related words, there may be edge cases where concept synonyms aren't fully detected.

## Assumptions

- The program assumes standard text formats (UTF-8 encoded) and might have issues with certain file encodings.
- Phone numbers are expected to follow the North American format or similar.

## Resources

- SpaCy Documentation: [https://spacy.io/](https://spacy.io/)
- Hugging Face Transformers: [https://huggingface.co/transformers/](https://huggingface.co/transformers/)
