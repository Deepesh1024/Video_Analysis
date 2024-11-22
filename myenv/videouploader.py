import streamlit as st
import os
from VideoTranscriber import VideoTranscriber
import json
from ResumeEvaluator import VideoResumeEvaluator
from trialposture import VideoAnalyzer
from newpdfgen import PDFReportGenerator
def process_video(video_file):
    st.video(video_file)
def process_video(video_file):
    output_audio_path = "audiofile.wav"
    output_json_path = "transcription_output.json"
    
    st.write("Transcribing the video...")
    transcriber = VideoTranscriber(video_file.name, output_audio_path, output_json_path)
    data = transcriber.transcribe()
    return data
    
def main():
    st.title("Video Document Uploader")
    evaluator = VideoResumeEvaluator()
    uploaded_video = st.file_uploader("Choose a video...", type=["mp4", "mov", "avi", "mkv"])
    
    if uploaded_video is not None:
        st.write("Extracting Video Data")
        analyzer = VideoAnalyzer(r"C:\Users\ayush\RE-LLM\myenv\23129_IraSinghal.mp4")
        analyzer.analyze()
        st.write("Video Extraction Done")
        st.write("Transcription Started")
        transcription_output = process_video(uploaded_video)
        st.write("Transcription Done")
        
        output = evaluator.evaluate_transcription(transcription_output)
        try:
            with open(r"C:\Users\ayush\RE-LLM\myenv\output.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        data["LLM"] = output

        with open(r"C:\Users\ayush\RE-LLM\myenv\output.json", 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
            print("Dumping Done")
        print("LLM Output inserted")
        st.write("Generating PDF")
        json_path = r"C:\Users\ayush\RE-LLM\myenv\output.json"
        pdf_path = "evaluation_report.pdf"
        pdf_generator = PDFReportGenerator(json_path, pdf_path)
        pdf_generator.create_pdf()
        with open(r"C:\Users\ayush\RE-LLM\myenv\evaluation_report.pdf", "rb") as pdf_file:
            st.download_button(
                label="Download PDF Report",
                data=pdf_file,
                file_name="evaluation_report.pdf",
                mime="application/pdf"
            )



    else : st.write("Video was not Uploaded")

if __name__ == "__main__":
    main()
