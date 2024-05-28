from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import pickle

df = pd.read_csv('spam.csv', encoding='utf-8-sig')[['status','content']]


df['status'] = df['status'].map({'ham': 0, 'spam': 1})



vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['content'])
y = df['status']

model = MultinomialNB()
model.fit(X, y)


with open('spam_model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

with open('vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)
