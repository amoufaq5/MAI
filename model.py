import tensorflow as tf
import os
import pickle

MODEL_PATH = 'model/myd_model.keras'
VECTORIZER_PATH = 'model/myd_vectorizer.pkl'

def build_model(text_vectorizer, vocab_size, embedding_dim=64, max_length=100):
    model = tf.keras.Sequential([
        text_vectorizer,
        tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, mask_zero=True),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')
    ])

    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def train_model(train_texts, train_labels, vocab_size=10000, embedding_dim=64, max_length=100, epochs=5):
    import numpy as np

    text_vectorizer = tf.keras.layers.TextVectorization(
        max_tokens=vocab_size,
        output_mode='int',
        output_sequence_length=max_length
    )

    train_texts = [t for t in train_texts if t.strip()]
    if len(train_texts) == 0:
        raise ValueError("All training texts are empty after cleaning.")

    text_vectorizer.adapt(train_texts)
    vocab = text_vectorizer.get_vocabulary()

    if len(vocab) <= 2:
        raise ValueError("Vocabulary too small after cleaning.")

    # Save vectorizer
    os.makedirs(os.path.dirname(VECTORIZER_PATH), exist_ok=True)
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump((text_vectorizer.get_config(), text_vectorizer.get_weights()), f)

    # Build model
    model = build_model(text_vectorizer, vocab_size, embedding_dim, max_length)

    # Convert to NumPy arrays
    train_texts_np = np.array(train_texts)
    train_labels_np = np.array(train_labels)

    # Train
    model.fit(train_texts_np, train_labels_np, epochs=epochs, validation_split=0.2)

    # Save model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save(MODEL_PATH)

    return model, text_vectorizer

