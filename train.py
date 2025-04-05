from data_loader import load_dataset, preprocess_data
from model import train_model

if __name__ == '__main__':
    # Path to your CSV dataset file (ensure the CSV is formatted as expected)
    csv_file = 'data.csv'
    df = load_dataset(csv_file)
    texts, labels = preprocess_data(df)
    
    # Train the model (adjust epochs and parameters as needed)
    model, vectorizer = train_model(texts, labels, epochs=5)
    print("Model training completed and saved.")
