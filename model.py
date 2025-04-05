import tensorflow as tf
import os
import pickle

# Define file paths for saving the model and vectorizer
MODEL_PATH = 'model/myd_model.h5'
VECTORIZER_PATH = 'model/myd_vectorizer.pkl'

def build_model(vocab_size, embedding_dim=64, max_length=100):
    model = tf.keras.Sequential([
        # The input layer will receive raw text
        tf.keras.layers.Input(shape=(None,), dtype=tf.string, name='text_input'),
        # Text vectorization layer converts text into integer tokens
        tf.keras.layers.TextVectorization(max_tokens=vocab_size, output_mode='int', output_sequence_length=max_length),
        tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, mask_zero=True),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')  # 2 classes: 0 = OTC safe, 1 = Refer doctor
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def train_model(train_texts, train_labels, vocab_size=10000, embedding_dim=64, max_length=100, epochs=10):
    # Create and adapt the text vectorization layer on training data
    vectorizer = tf.keras.layers.TextVectorization(max_tokens=vocab_size, output_mode='int', output_sequence_length=max_length)
    vectorizer.adapt(train_texts)
    
    # Save vectorizer configuration and weights for later use
    vectorizer_config = vectorizer.get_config()
    vectorizer_weights = vectorizer.get_weights()
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump((vectorizer_config, vectorizer_weights), f)
    
    # Build and train the model
    model = build_model(vocab_size, embedding_dim, max_length)
    # Update the text vectorization layer’s weights to match our adapted vectorizer
    model.layers[1].set_weights(vectorizer_weights)
    
    model.fit(train_texts, train_labels, epochs=epochs, validation_split=0.2)
    
    # Save the trained model to disk
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save(MODEL_PATH)
    return model, vectorizer

def load_vectorizer():
    # Load vectorizer configuration and weights from disk
    with open(VECTORIZER_PATH, 'rb') as f:
        config, weights = pickle.load(f)
    vectorizer = tf.keras.layers.TextVectorization.from_config(config)
    vectorizer.set_weights(weights)
    return vectorizer

def load_trained_model():
    # Load the trained model and associated vectorizer
    model = tf.keras.models.load_model(MODEL_PATH)
    vectorizer = load_vectorizer()
    return model, vectorizer

def predict_diagnosis(input_text, model, vectorizer):
    # Given an input text, predict whether an OTC recommendation is safe or if a doctor referral is needed.
    # The model expects a list of string inputs.
    prediction = model.predict([input_text])
    predicted_class = prediction.argmax(axis=-1)[0]
    # 0 = OTC recommendation, 1 = Refer doctor
    return predicted_class, prediction[0]
