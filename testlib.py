import nltk
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

from nltk.tokenize import sent_tokenize
text = "This is a test. Let's check if sentence tokenization works."
print(sent_tokenize(text))
