import streamlit as st
print("Done1")
import os
print("Done1")
from newtranscriber import VideoTranscriber
print("Done1")
import json
print("Done1")
from ResumeEvaluator import VideoResumeEvaluator
print("Done1")
# from trialposture import VideoAnalyzer
from groqvision2 import VideoAnalyzer
print("Done1")
from newpdfgen import PDFReportGenerator
print("Done1")




    
def process_video(video_file):
    st.video(video_file)
    output_audio_path = "audiofile.wav"
    output_json_path = "transcription_output.json"
    
    st.write("Transcribing the video...")
    transcriber = VideoTranscriber(video_file, output_audio_path, output_json_path)
    data = transcriber.transcribe()
    return data
    
def main():
    st.title("Video Document Uploader")
    evaluator = VideoResumeEvaluator()
    uploaded_video = st.file_uploader("Choose a video...", type=["mp4", "mov", "avi", "mkv"])
    
    if uploaded_video is not None:
        st.write("Extracting Video Data")
        analyzer = VideoAnalyzer(uploaded_video)
        analyzer.analyze_video()
        st.write("Video Extraction Done")
        st.write("Transcription Started")
        transcription_output = process_video(uploaded_video)
        st.write("Transcription Done")
        
        output = evaluator.evaluate_transcription(transcription_output)
        try:
            with open(r"transcription_output.json", "r") as f:
                data = json.load(f)
        except Exception as e:
            raise e
        
        with open(r"output.json", 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        data['LLM'] = output

        with open(r"output.json", 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
            print("Dumping Done")
        print("LLM Output inserted")
        st.write("Generating PDF")
        json_path = r"output.json"
        pdf_path = "evaluation_report.pdf"
        pdf_generator = PDFReportGenerator(json_path, pdf_path)
        pdf_generator.create_pdf()
        with open(r"evaluation_report.pdf", "rb") as pdf_file:
            st.download_button(
                label="Download PDF Report",
                data=pdf_file,
                file_name="evaluation_report.pdf",
                mime="application/pdf"
            )



    else : st.write("Video was not Uploaded")

if __name__ == "__main__":
    main()
