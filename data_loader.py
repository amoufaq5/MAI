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
    
    # Drop rows with missing or empty 'symptoms' or 'overview'
    df_otc = df_otc.dropna(subset=['symptoms', 'overview'])
    df_otc = df_otc[(df_otc['symptoms'].str.strip() != '') & (df_otc['overview'].str.strip() != '')]
    
    print("Filtered dataset shape:", df_otc.shape)
    print("First few rows of filtered data:")
    print(df_otc.head())
    
    return df_otc

def preprocess_data(df):
    # Check for expected columns
    if 'symptoms' not in df.columns or 'overview' not in df.columns:
        raise KeyError("Expected columns 'symptoms' and 'overview' not found in the dataset.")
    
    # Combine 'symptoms' and 'overview' into a single text field for model input
    df['text'] = df['symptoms'] + ' ' + df['overview']
    # Since the dataset is OTC only, label these as 0 (OTC safe)
    df['label'] = 0
    texts = df['text'].tolist()
    labels = df['label'].tolist()
    
    print("Sample training texts:")
    for text in texts[:5]:
        print(text)
    
    return texts, labels

if __name__ == '__main__':
    # Update the file path as needed (e.g., 'data/dataset.csv' or 'data.csv')
    csv_file_path = 'data/dataset.csv'
    df_otc = load_dataset(csv_file_path)
    texts, labels = preprocess_data(df_otc)
