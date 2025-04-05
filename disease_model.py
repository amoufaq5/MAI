import pandas as pd
import json
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

MODEL_FILE = "disease_classifier.joblib"
VECTORIZER_FILE = "vectorizer.joblib"
DISEASE_DB_FILE = "symptom_disease_dataset.csv"

def train_disease_model():
    df = pd.read_csv(DISEASE_DB_FILE)
    texts = df["symptoms"]
    labels = df["disease"]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    model = MultinomialNB()
    model.fit(X, labels)

    joblib.dump(model, MODEL_FILE)
    joblib.dump(vectorizer, VECTORIZER_FILE)

    print("✅ Disease model trained and saved.")

def predict_disease(symptom_input):
    model = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)

    X = vectorizer.transform([symptom_input])
    prediction = model.predict(X)[0]
    probs = model.predict_proba(X)[0]
    confidence = round(max(probs) * 100, 2)
    return prediction, confidence
