from moviepy.editor import VideoFileClip
import whisper
import json

class VideoTranscriber:
    def __init__(self, video_path, output_audio_path, output_json_path):
        self.video_path = video_path
        self.output_audio_path = output_audio_path
        self.output_json_path = output_json_path
        self.model = whisper.load_model("small")

    def extract_audio(self):
        """Extract audio from video file and save it."""
        video = VideoFileClip(self.video_path)
        audio = video.audio
        audio.write_audiofile(self.output_audio_path)

    def transcribe(self):
        """Transcribe audio and save the results to a JSON file."""
        self.extract_audio()  # Extract audio before transcribing
        results = self.model.transcribe(self.output_audio_path, verbose=True)
        transcription_output = []
        data = ""
        for segment in results['segments']:
            start = segment['start']
            end = segment['end']
            text = segment['text']
            
            # Print the transcription to console
            print(f"[{start:.2f}s - {end:.2f}s] {text}")
            data += f"[{start:.2f}s - {end:.2f}s] {text}"

            # Append the segment information to the list
            transcription_output.append({
                'start': start,
                'end': end,
                'text': text
            })

        # Write the transcription results to a JSON file
        with open(self.output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(transcription_output, json_file, ensure_ascii=False, indent=4)

        print(f"Transcription results saved to {self.output_json_path}")
        return data 
