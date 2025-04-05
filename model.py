import tensorflow as tf
import os
import pickle

MODEL_PATH = 'model/myd_model.h5'
VECTORIZER_PATH = 'model/myd_vectorizer.pkl'

def build_model(vocab_size, embedding_dim=64, max_length=100):
    model = tf.keras.Sequential([
        # Input: raw text strings
        tf.keras.layers.Input(shape=(None,), dtype=tf.string, name='text_input'),
        # Convert text to integer tokens
        tf.keras.layers.TextVectorization(
            max_tokens=vocab_size,
            output_mode='int',
            output_sequence_length=max_length
        ),
        tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, mask_zero=True),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')  # Two classes: 0 = OTC safe, 1 = Refer doctor
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def safe_get_vocabulary(vectorizer):
    """
    Attempts to retrieve the vocabulary from the TextVectorization layer.
    If a UnicodeDecodeError occurs, falls back to extracting the vocabulary
    from the underlying lookup table.
    """
    try:
        # Try to get the vocabulary normally
        raw_vocab = vectorizer.get_vocabulary()
        vocab = []
        for token in raw_vocab:
            try:
                vocab.append(tf.compat.as_text(token, vectorizer.encoding))
            except Exception:
                vocab.append('')
        return vocab
    except UnicodeDecodeError:
        # Fallback: use the underlying lookup table to export the keys
        table = vectorizer._lookup_layer._table  # Access the private table
        keys_tensor, _ = table.export()  # export returns (keys, values)
        raw_vocab = keys_tensor.numpy().tolist()
        vocab = []
        for token in raw_vocab:
            try:
                if isinstance(token, bytes):
                    vocab.append(token.decode('utf-8', errors='ignore'))
                else:
                    vocab.append(token)
            except Exception:
                vocab.append('')
        return vocab

def train_model(train_texts, train_labels, vocab_size=10000, embedding_dim=64, max_length=100, epochs=10):
    # Ensure all texts are strings
    train_texts = [str(t) for t in train_texts]
    
    # Create and adapt the TextVectorization layer on the training texts
    vectorizer = tf.keras.layers.TextVectorization(
        max_tokens=vocab_size,
        output_mode='int',
        output_sequence_length=max_length
    )
    vectorizer.adapt(train_texts)
    
    # Retrieve the vocabulary using our safe helper
    vocab = safe_get_vocabulary(vectorizer)
    
    # Save the vectorizer configuration and vocabulary
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump((vectorizer.get_config(), vocab), f)
    
    # Build the model and set the vectorization layer's vocabulary
    model = build_model(vocab_size, embedding_dim, max_length)
    model.layers[1].set_vocabulary(vocab)
    
    # Train the model
    model.fit(train_texts, train_labels, epochs=epochs, validation_split=0.2)
    
    # Save the trained model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save(MODEL_PATH)
    return model, vectorizer

def load_vectorizer():
    # Load configuration and vocabulary from file
    with open(VECTORIZER_PATH, 'rb') as f:
        config, vocab = pickle.load(f)
    vectorizer = tf.keras.layers.TextVectorization.from_config(config)
    vectorizer.set_vocabulary(vocab)
    return vectorizer

def load_trained_model():
    # Load the saved model and vectorizer
    model = tf.keras.models.load_model(MODEL_PATH)
    vectorizer = load_vectorizer()
    return model, vectorizer

def predict_diagnosis(input_text, model, vectorizer):
    # Given an input text, predict whether OTC is safe or a referral is needed.
    prediction = model.predict([input_text])
    predicted_class = prediction.argmax(axis=-1)[0]
    return predicted_class, prediction[0]
