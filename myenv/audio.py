from moviepy.editor import VideoFileClip
import whisper
import json
model = whisper.load_model("small")


def extract_audio_from_video(video_path, output_audio_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path)


video_path = r"C:\Users\ayush\RE-LLM\myenv\compresseddhruv.mp4"
output_audio_path = r"C:\Users\ayush\RE-LLM\myenv\audiofile.wav"
extract_audio_from_video(video_path, output_audio_path)
results = model.transcribe(output_audio_path, verbose=True)
transcription_output = []
for segment in results['segments']:
    start = segment['start']
    end = segment['end']
    text = segment['text']

    # Print the transcription to console
    print(f"[{start:.2f}s - {end:.2f}s] {text}")

    # Append the segment information to the list
    transcription_output.append({
        'start': start,
        'end': end,
        'text': text
    })
    # Specify the output JSON file path
output_json_path = r"C:\Users\ayush\RE-LLM\myenv\audiofile.wav"

# Write the transcription results to a JSON file
with open(output_json_path, 'w', encoding='utf-8') as json_file:
    json.dump(transcription_output, json_file, ensure_ascii=False, indent=4)

print(f"Transcription results saved to {output_json_path}")

