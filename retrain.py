import os
import json
from data_loader import load_dataset, preprocess_data
from model import train_model
from sklearn.preprocessing import LabelEncoder

FEEDBACK_FILE = "feedback.json"
CSV_PATH = "data/dataset.csv"

def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        print("No feedback found. Skipping.")
        return [], []

    with open(FEEDBACK_FILE, "r") as f:
        data = json.load(f)

    new_texts = []
    new_labels = []

    for entry in data:
        if entry["feedback"] == "correction":
            new_texts.append(entry["input"])
            new_labels.append(entry["correct_drug"])
        elif entry["feedback"] == "positive":
            new_texts.append(entry["input"])
            new_labels.append(entry["predicted_drug"])

    print(f"✅ Loaded {len(new_texts)} feedback entries.")
    return new_texts, new_labels

def main():
    # Load original OTC dataset
    df = load_dataset(CSV_PATH)
    texts, labels = preprocess_data(df)

    # Convert numeric OTC label 0 to drug names
    drug_names = df["drug name"].tolist()

    # Override original numeric labels with drug names for compatibility
    labels = drug_names

    # Load feedback
    feedback_texts, feedback_labels = load_feedback()
    texts += feedback_texts
    labels += feedback_labels

    print(f"📊 Final training set size: {len(texts)} entries")

    # Train and save the model
    model, vectorizer, encoder = train_model(texts, labels, epochs=5)
    print("✅ Retraining complete. Model updated.")

if __name__ == "__main__":
    main()
