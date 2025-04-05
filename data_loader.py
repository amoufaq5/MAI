import pandas as pd
import re

def load_dataset(csv_file_path):
    # Load the CSV file
    df = pd.read_csv(csv_file_path)

    # Normalize column names: strip whitespace and convert to lowercase
    df.columns = df.columns.str.strip().str.lower()
    print("📌 Columns in dataset:", df.columns.tolist())

    # Detect drug type column name
    if 'drug type' in df.columns:
        drug_col = 'drug type'
    elif 'drug_type' in df.columns:
        drug_col = 'drug_type'
    elif 'drugtype' in df.columns:
        drug_col = 'drugtype'
    else:
        raise KeyError("❌ No column found for 'drug type' (or equivalent). Available columns: " + ", ".join(df.columns))

    # Filter only OTC drugs
    df_otc = df[df[drug_col].str.upper() == 'OTC']

    # Drop rows missing critical info
    df_otc = df_otc.dropna(subset=['symptoms', 'overview'])
    df_otc = df_otc[(df_otc['symptoms'].str.strip() != '') & (df_otc['overview'].str.strip() != '')]

    print("✅ Filtered dataset shape:", df_otc.shape)
    print("🧪 Sample filtered data:")
    print(df_otc[['symptoms', 'overview', drug_col]].head())

    return df_otc

def preprocess_data(df):
    # Check that necessary columns are present
    if 'symptoms' not in df.columns or 'overview' not in df.columns:
        raise KeyError("❌ Expected columns 'symptoms' and 'overview' not found in the dataset.")
    
    # Combine text fields
    combined_text = df['symptoms'] + ' ' + df['overview']

    # Clean the text: lowercase, strip, remove special characters
    cleaned_text = combined_text.str.lower().apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x)).str.strip()

    # Filter out empty strings
    df = df[cleaned_text != '']
    df['text'] = cleaned_text

    # Label as 0 (safe for OTC)
    df['label'] = 0

    # Convert to lists
    texts = df['text'].tolist()
    labels = df['label'].tolist()

    print("✅ Sample cleaned training texts:")
    for text in texts[:5]:
        print("🟢", text)

    return texts, labels

# Optional: for testing directly
if __name__ == '__main__':
    # Replace with your dataset path
    csv_file_path = 'data/dataset.csv'
    df_otc = load_dataset(csv_file_path)
    texts, labels = preprocess_data(df_otc)
