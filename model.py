import tensorflow as tf
import os
import pickle

MODEL_PATH = 'model/myd_model.h5'
VECTORIZER_PATH = 'model/myd_vectorizer.pkl'

def build_model(vocab_size, embedding_dim=64, max_length=100):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(None,), dtype=tf.string, name='text_input'),
        tf.keras.layers.TextVectorization(
            max_tokens=vocab_size,
            output_mode='int',
            output_sequence_length=max_length
        ),
        tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, mask_zero=True),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')  # 2 output classes
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def train_model(train_texts, train_labels, vocab_size=10000, embedding_dim=64, max_length=100, epochs=5):
    # Create and adapt the text vectorization layer
    text_vectorizer = tf.keras.layers.TextVectorization(
        max_tokens=vocab_size,
        output_mode='int',
        output_sequence_length=max_length
    )

    # SAFEGUARD: Filter out empty strings before adapting
    train_texts = [t for t in train_texts if t.strip()]
    if len(train_texts) == 0:
        raise ValueError("All training texts are empty after cleaning.")

    text_vectorizer.adapt(train_texts)
    vocab = text_vectorizer.get_vocabulary()

    if len(vocab) <= 2:
        raise ValueError("Vocabulary is too small after processing. Check dataset for valid tokens.")

    # Save vectorizer config + weights
    os.makedirs(os.path.dirname(VECTORIZER_PATH), exist_ok=True)
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump((text_vectorizer.get_config(), text_vectorizer.get_weights()), f)

    # Build model and assign weights to vectorizer layer inside it
    model = build_model(vocab_size, embedding_dim, max_length)
    model.layers[1].set_weights(text_vectorizer.get_weights())

    model.fit(train_texts, train_labels, epochs=epochs, validation_split=0.2)

    # Save model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save(MODEL_PATH)
    return model, text_vectorizer
