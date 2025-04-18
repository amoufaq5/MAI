# predictor.py
import joblib
import numpy as np

# Load trained models
model = joblib.load("disease_classifier.joblib")
vectorizer = joblib.load("vectorizer.joblib")


def predict_top_diseases(text, threshold=0.75, top_n=3):
    X = vectorizer.transform([text])
    probs = model.predict_proba(X)[0]
    classes = model.classes_

    # Pair diseases with probabilities
    disease_scores = [(disease, prob * 100) for disease, prob in zip(classes, probs)]
    # Filter and sort
    filtered = [item for item in disease_scores if item[1] >= (threshold * 100)]
    top_diseases = sorted(filtered, key=lambda x: x[1], reverse=True)[:top_n]

    return top_diseases
