import os
import pickle
import numpy as np
import tensorflow as tf

# Use the new Keras format or SavedModel directory
MODEL_PATH = 'model/myd_model.keras'  # You can also use: 'model/myd_model'
VECTORIZER_PATH = 'model/myd_vectorizer.pkl'


def build_model(text_vectorizer, vocab_size=10000, embedding_dim=64, max_length=100):
    model = tf.keras.Sequential([
        text_vectorizer,
        tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, mask_zero=True),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')  # 2 classes: OTC or Refer
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def train_model(train_texts, train_labels, vocab_size=10000, embedding_dim=64, max_length=100, epochs=5):
    # Clean and verify text
    train_texts = [t for t in train_texts if t.strip()]
    if len(train_texts) == 0:
        raise ValueError("All training texts are empty after cleaning.")

    # Create and adapt the vectorizer
    text_vectorizer = tf.keras.layers.TextVectorization(
        max_tokens=vocab_size,
        output_mode='int',
        output_sequence_length=max_length
    )
    text_vectorizer.adapt(train_texts)

    # Save vectorizer config and weights
    os.makedirs(os.path.dirname(VECTORIZER_PATH), exist_ok=True)
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump((text_vectorizer.get_config(), text_vectorizer.get_weights()), f)

    # Build model
    model = build_model(text_vectorizer, vocab_size, embedding_dim, max_length)

    # Convert to NumPy arrays for training
    train_texts_np = np.array(train_texts)
    train_labels_np = np.array(train_labels)

    # Train model
    model.fit(train_texts_np, train_labels_np, epochs=epochs, validation_split=0.2)

    # Save model (use .keras or SavedModel format)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save(MODEL_PATH)

    print(f"✅ Model trained and saved to: {MODEL_PATH}")
    return model, text_vectorizer


def load_vectorizer():
    with open(VECTORIZER_PATH, 'rb') as f:
        config, weights = pickle.load(f)
    vectorizer = tf.keras.layers.TextVectorization.from_config(config)
    vectorizer.set_weights(weights)
    return vectorizer


def load_trained_model():
    model = tf.keras.models.load_model(MODEL_PATH)
    vectorizer = load_vectorizer()
    return model, vectorizer


def predict_diagnosis(input_text, model, vectorizer):
    prediction = model.predict([input_text])
    predicted_class = prediction.argmax(axis=-1)[0]
    return predicted_class, prediction[0]
