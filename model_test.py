import numpy as np
import librosa
import warnings
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load model and label encoder
model_path = "model.h5"
model = load_model(model_path)
le = LabelEncoder()
le.classes_ = np.array(['happy', 'sad', 'neutral'])

def extract_mfcc(audio_path, max_len=40):
    """Extract MFCC features from an audio file"""
    signal, sample_rate = librosa.load(audio_path, sr=None)
    mfcc = librosa.feature.mfcc(y=signal, sr=sample_rate, n_mfcc=13)
    
    if mfcc.shape[1] < max_len:
        pad_width = max_len - mfcc.shape[1]
        mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
    else:
        mfcc = mfcc[:, :max_len]
    return mfcc

def predict_emotion(audio_path, model, label_encoder):
    """Predict emotion from audio file"""
    mfcc_2d = extract_mfcc(audio_path, max_len=40)
    mfcc_4d = mfcc_2d[np.newaxis, ..., np.newaxis]
    predictions = model.predict(mfcc_4d)
    
    class_index = np.argmax(predictions, axis=-1)[0]
    predicted_label = label_encoder.inverse_transform([class_index])[0]
    return predicted_label

def predict_tone(file_path: str):
    """
    Predict tone from audio file and return detailed analysis
    """
    try:
        # Get the basic emotion prediction
        predicted_emotion = predict_emotion(file_path, model, le)
        
        # Map emotions to detailed tone analysis
        tone_mapping = {
            'happy': {
                'Overall Tone': 'positive and enthusiastic',
                'Emotional Range': 'Displays enthusiasm and energy',
                'Voice Modulation': 'Dynamic and expressive',
                'Engagement Level': 'Highly engaging'
            },
            'sad': {
                'Overall Tone': 'subdued and reflective',
                'Emotional Range': 'Shows depth and sincerity',
                'Voice Modulation': 'Measured and thoughtful',
                'Engagement Level': 'Contemplative engagement'
            },
            'neutral': {
                'Overall Tone': 'professional and balanced',
                'Emotional Range': 'Maintained consistent professional tone',
                'Voice Modulation': 'Well-measured and clear',
                'Engagement Level': 'Steady and focused'
            }
        }
        
        # Return the detailed tone analysis
        return tone_mapping.get(predicted_emotion, tone_mapping['neutral'])
        
    except Exception as e:
        print(f"Error in tone prediction: {str(e)}")
        # Return default values if prediction fails
        return {
            'Overall Tone': 'professional and balanced',
            'Emotional Range': 'Maintained consistent professional tone',
            'Voice Modulation': 'Well-measured and clear',
            'Engagement Level': 'Steady and focused'
        }