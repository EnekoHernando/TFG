from gensim.models import Word2Vec
sentences = [["hello", "world"], ["machine", "learning"]]
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)
print(model.wv['hello'])
