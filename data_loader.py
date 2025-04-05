import pandas as pd

def load_dataset(csv_file_path):
    # Load the CSV file
    df = pd.read_csv(csv_file_path)
    # Normalize column names: strip whitespace and convert to lower-case
    df.columns = df.columns.str.strip().str.lower()
    print("Columns in dataset:", df.columns.tolist())

    # Check for possible column names for drug type
    if 'drug type' in df.columns:
        drug_col = 'drug type'
    elif 'drug_type' in df.columns:
        drug_col = 'drug_type'
    elif 'drugtype' in df.columns:
        drug_col = 'drugtype'
    else:
        raise KeyError("No column found for 'drug type' (or equivalent). Available columns: " + ", ".join(df.columns))

    # Filter rows to include only OTC data (assuming the value is 'OTC' in upper-case)
    df_otc = df[df[drug_col].str.upper() == 'OTC']
    return df_otc

def preprocess_data(df):
    # Combine relevant text fields for input to the model; here we use 'symptoms' and 'overview'
    # Also normalize column names for these fields to ensure consistency
    if 'symptoms' not in df.columns or 'overview' not in df.columns:
        raise KeyError("Expected columns 'symptoms' and 'overview' not found in the dataset.")
    df['text'] = df['symptoms'] + ' ' + df['overview']
    # Since the dataset is OTC only, label these as 0 (OTC safe)
    df['label'] = 0
    texts = df['text'].tolist()
    labels = df['label'].tolist()
    return texts, labels

if __name__ == '__main__':
    # For testing purposes: update the file path as needed
    csv_file_path = 'data/dataset.csv'  # or 'data.csv' if placed in project root
    df_otc = load_dataset(csv_file_path)
    print("Filtered dataset shape:", df_otc.shape)
