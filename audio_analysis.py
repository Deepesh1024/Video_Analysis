import json
import re
from pydub import AudioSegment

def analyze_audio_metrics(audio_path, transcription_json_path):
    """
    Analyze the audio file to calculate the average volume (in dBFS)
    and speaking pace (words per minute) based on the actual speaking duration.
    """
    # Load the audio file
    audio = AudioSegment.from_file(audio_path)
    average_volume = audio.dBFS  # Average volume in dBFS

    # Load the transcription JSON
    with open(transcription_json_path, 'r') as f:
        transcription_data = json.load(f)

    # Sum up total speaking time (seconds) using segment timestamps
    speaking_time_seconds = 0.0
    for segment in transcription_data:
        start_time = segment.get('start', 0)
        end_time = segment.get('end', 0)
        speaking_time_seconds += (end_time - start_time)

    # Convert speaking time to minutes
    speaking_time_minutes = speaking_time_seconds / 60.0 if speaking_time_seconds > 0 else 1.0

    # Count total words in the transcription
    full_text = " ".join(segment.get("text", "") for segment in transcription_data)
    words = re.findall(r'\w+', full_text)
    total_words = len(words)

    # Calculate words per minute (based on speaking time)
    words_per_minute = total_words / speaking_time_minutes if speaking_time_minutes > 0 else 0.0

    return {
        "average_volume": average_volume,
        "words_per_minute": words_per_minute
    }
