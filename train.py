from data_loader import load_dataset, preprocess_data
from model import train_model

if __name__ == '__main__':
    csv_file = 'data/dataset.csv'
    df = load_dataset(csv_file)

    # use drug name as label
    df['label'] = df['drug name']
    texts = df['symptoms'].fillna('') + ' ' + df['overview'].fillna('')
    texts = texts.str.lower().str.replace(r'[^a-zA-Z0-9\s]', '', regex=True).str.strip().tolist()
    labels = df['label'].tolist()

    train_model(texts, labels, epochs=5)
