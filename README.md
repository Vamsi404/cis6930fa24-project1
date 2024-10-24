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

1. Install the required Python packages using pip:
   ```bash
   pipenv install -e
   ```
2. Download necessary SpaCy models:
   ```bash
   pipenv python -m spacy download en_core_web_md
   ```

## Tests & Running the Tests

1. **Test Censor Names**: Checks if all names (PERSON entities) are correctly censored using spaCy and Hugging Face pipelines.

2. **Test Censor Dates**: Validates correct censoring of various date formats, including custom patterns.

3. **Test Censor Phone Numbers**: Ensures phone numbers in multiple formats are detected and censored.

4. **Test Censor Addresses**: Confirms that organization names, locations, and addresses are censored.

5. **Test Concept Censoring**: Verifies censoring of sentences containing specific concepts (e.g., “prison”).

6. **Test Statistics Generation**: Ensures accurate reporting of censored entities (names, dates, etc.) in statistics.

7. **Test Multiple Input Files**: Checks consistent censoring across multiple input files.

8. **Test Output to stderr/stdout**: Ensures statistics are correctly printed to stderr or stdout when specified.

These shorter descriptions still cover the key aspects of each test.

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
