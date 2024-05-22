import spacy
nlp = spacy.load("es_core_news_sm")
doc = nlp("ChatGPT es un modelo de lenguaje.")
tokens = [token.text for token in doc]
print(tokens)