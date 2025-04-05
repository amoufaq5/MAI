import os
import pickle
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder

MODEL_PATH = 'model/myd_model.keras'
VECTORIZER_PATH = 'model/myd_vectorizer.pkl'
ENCODER_PATH = 'model/label_encoder.pkl'

def build_model(text_vectorizer, vocab_size=10000, embedding_dim=64, max_length=100, num_classes=10):
    model = tf.keras.Sequential([
        text_vectorizer,
        tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, mask_zero=True),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def train_model(train_texts, train_labels, vocab_size=10000, embedding_dim=64, max_length=100, epochs=5):
    from sklearn.preprocessing import LabelEncoder

    text_vectorizer = tf.keras.layers.TextVectorization(
        max_tokens=vocab_size,
        output_mode='int',
        output_sequence_length=max_length
    )
    train_texts = [t for t in train_texts if t.strip()]
    text_vectorizer.adapt(train_texts)

    # Label encode the drug names
    encoder = LabelEncoder()
    train_labels_encoded = encoder.fit_transform(train_labels)

    os.makedirs(os.path.dirname(VECTORIZER_PATH), exist_ok=True)
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump((text_vectorizer.get_config(), text_vectorizer.get_weights()), f)

    with open(ENCODER_PATH, 'wb') as f:
        pickle.dump(encoder, f)

    num_classes = len(encoder.classes_)
    model = build_model(text_vectorizer, vocab_size, embedding_dim, max_length, num_classes)

    model.fit(np.array(train_texts), np.array(train_labels_encoded), epochs=epochs, validation_split=0.2)
    model.save(MODEL_PATH, save_format='keras')

    print("✅ Model trained and saved.")
    return model, text_vectorizer, encoder

def load_vectorizer():
    with open(VECTORIZER_PATH, 'rb') as f:
        config, weights = pickle.load(f)
    vectorizer = tf.keras.layers.TextVectorization.from_config(config)
    vectorizer.set_weights(weights)
    return vectorizer

def load_encoder():
    with open(ENCODER_PATH, 'rb') as f:
        encoder = pickle.load(f)
    return encoder
