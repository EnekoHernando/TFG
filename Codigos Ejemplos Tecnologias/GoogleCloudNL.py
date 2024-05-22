from google.cloud import language_v1
client = language_v1.LanguageServiceClient()
document = language_v1.Document(content="I am very happy.", type_=language_v1.Document.Type.PLAIN_TEXT)
sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment
print(f"Score: {sentiment.score}, Magnitude: {sentiment.magnitude}")
