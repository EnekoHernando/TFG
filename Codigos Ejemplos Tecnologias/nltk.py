import nltk
nltk.download('punkt')
text = "ChatGPT es un modelo de lenguaje."
tokens = nltk.word_tokenize(text)
print(tokens)
tagged = nltk.pos_tag(tokens)
print(tagged)