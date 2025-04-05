import tensorflow as tf
import os
import pickle

MODEL_PATH = 'model/myd_model.h5'
VECTORIZER_PATH = 'model/myd_vectorizer.pkl'

def build_model(vocab_size, embedding_dim=64, max_length=100):
    model = tf.keras.Sequential([
        # Input layer receives raw text strings
        tf.keras.layers.Input(shape=(None,), dtype=tf.string, name='text_input'),
        # TextVectorization converts text to integer tokens
        tf.keras.layers.TextVectorization(max_tokens=vocab_size,
                                          output_mode='int',
                                          output_sequence_length=max_length),
        tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, mask_zero=True),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')  # Two classes: 0 = OTC safe, 1 = Refer doctor
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def train_model(train_texts, train_labels, vocab_size=10000, embedding_dim=64, max_length=100, epochs=10):
    # Ensure all texts are strings
    train_texts = [str(t) for t in train_texts]
    
    # Create and adapt the TextVectorization layer on the training texts
    vectorizer = tf.keras.layers.TextVectorization(max_tokens=vocab_size,
                                                   output_mode='int',
                                                   output_sequence_length=max_length)
    vectorizer.adapt(train_texts)
    
    # Try to extract the vocabulary using get_vocabulary()
    try:
        raw_vocab = vectorizer.get_vocabulary()
    except UnicodeDecodeError:
        # Fallback: try to access the internal _vocab attribute directly
        raw_vocab = vectorizer._lookup_layer._vocab

    # Process the raw vocabulary safely
    vocab = []
    for token in raw_vocab:
        if isinstance(token, bytes):
            try:
                decoded = token.decode('utf-8', errors='ignore')
            except Exception:
                decoded = ''
            vocab.append(decoded)
        else:
            vocab.append(token)
    
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
