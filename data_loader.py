import pandas as pd

def load_dataset(csv_file_path):
    # Load CSV dataset (ensure your CSV file has columns like disease, symptoms, interactions, overview, drug type, side effects)
    df = pd.read_csv(csv_file_path)
    # Filter rows to include only OTC data (assuming 'drug type' indicates OTC in uppercase)
    df_otc = df[df['drug type'].str.upper() == 'OTC']
    return df_otc

def preprocess_data(df):
    # Combine relevant text fields for input to the model; here we use 'symptoms' and 'overview'
    df['text'] = df['symptoms'] + ' ' + df['overview']
    # Since the dataset is OTC only, label these as 0 (OTC safe). 
    # In a full system you might include a secondary set of examples for referral decisions.
    df['label'] = 0
    texts = df['text'].tolist()
    labels = df['label'].tolist()
    return texts, labels
