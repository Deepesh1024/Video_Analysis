import streamlit as st
import os
import json
from newtranscriber import VideoTranscriber
from Overall_Analyser import VideoResumeEvaluator
from VideoEvaluation import VideoAnalyzer 
from Qualitatitive_analyser import VideoResumeEvaluator2  # Ensure filename matches exactly
from PDF_Generator import create_combined_pdf
from audio_analysis import analyze_audio_metrics  # New import for audio analysis

st.set_page_config(
    page_title="Video Analysis & Report Generator",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
    .step-container {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def process_video(video_file):
    st.video(video_file)
    output_audio_path = "audiofile.wav"
    output_json_path = "json/transcription_output.json"

    st.write("### Step 2: Transcribing the video...")
    with st.spinner("Transcribing... Please wait."):
        transcriber = VideoTranscriber(video_file, output_audio_path, output_json_path)
        data = transcriber.transcribe()
    st.success("Transcription completed successfully!")
    return data

def main():
    # Sidebar
    st.sidebar.header("Navigation")
    st.sidebar.markdown("""
    - **Upload Video**: Analyze and generate a report
    - **About**: Learn more about this tool
    """)
    
    st.sidebar.image("logos/logo.png", caption="School of Meaningful Experiences")
    
    # Tips section in sidebar
    st.sidebar.markdown("### 💡 Tips for Best Results")
    st.sidebar.info("""
    - Ensure good lighting and clear audio
    - Speak clearly and at a moderate pace
    - Keep the video between 2-5 minutes
    - Face the camera directly
    - Use professional attire
    """)
    
    # Main content
    st.title("🎥 Video Resume Analyzer & Report Generator")
    st.write("""
        **Analyze your video resume with advanced AI tools**. 
        This app extracts insights from your video, transcribes it, evaluates it, and generates a professional PDF report.
    """)
    
    # User Name Input
    user_name = st.text_input("Enter your name:", "", key="user_name")
    if not user_name:
        st.warning("Name is required before uploading a video.")
        st.stop()
    
    # How to use section
    with st.expander("How to use this tool?", expanded=False):
        st.markdown("""
        1. Upload your video in one of the supported formats (MP4, MOV, AVI, MKV)
        2. The app will automatically:
           - Analyze the video content and presentation
           - Transcribe the speech to text
           - Evaluate the content and tone using AI
           - Generate a comprehensive PDF report
        3. Download your PDF report to review the insights
        """)

    uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
    
    if uploaded_video is not None:
        st.markdown("---")
        
        # Step 1: Video Analysis
        with st.container():
            st.write("### Step 1: Extracting insights from the video...")
            with st.spinner("Analyzing video... Please wait."):
                analyzer = VideoAnalyzer(uploaded_video)
                output = analyzer.analyze_video()
                with open("json/output.json", 'w', encoding='utf-8') as json_file:
                    json.dump(output, json_file, ensure_ascii=False, indent=4)
            st.success("Video analysis completed successfully!")
        
        # Step 2: Transcription
        transcription_output = process_video(uploaded_video)
        
        # Step 2.5: Audio Analysis - Volume and Pace
        with st.container():
            st.write("### Step 2.5: Audio Analysis - Volume and Pace")
            audio_metrics = analyze_audio_metrics("audiofile.wav", "json/transcription_output.json")
            volume_dbfs = audio_metrics["average_volume"]
            # Convert the dBFS value to an approximate percentage (assuming -60 dBFS ~ silence and 0 dBFS ~ max)
            volume_percentage = ((volume_dbfs + 60) / 60) * 100
            st.write(f"**Average Volume:** {volume_dbfs:.2f} dBFS (approx {volume_percentage:.0f}% of maximum loudness)")
            st.write(f"**Speaking Pace:** {audio_metrics['words_per_minute']:.2f} words per minute")

            # Save volume & pace to output.json for PDF
            with open("json/output.json", "r") as f:
                data = json.load(f)
            data["average_volume"] = volume_dbfs
            data["speaking_pace"] = audio_metrics["words_per_minute"]
            data["average_volume_percentage"] = volume_percentage
            with open("json/output.json", "w") as f:
                json.dump(data, f, indent=4)
        
        # Step 3: Content & Tone Evaluation
        with st.container():
            st.write("### Step 3: Evaluating content and tone...")
            evaluator = VideoResumeEvaluator()
            quality_evaluator = VideoResumeEvaluator2()
            
            try:
                with st.spinner("Analyzing content..."):
                    eval_results = evaluator.evaluate_transcription(transcription_output)
                    quality_evaluator.evaluate_transcription(transcription_output)
                
                with open("json/output.json", 'r') as f:
                    data = json.load(f)
                
                data.update({
                    'User Name': user_name,
                    'LLM': eval_results
                })
                
                # Save updated data
                with open("json/output.json", 'w') as f:
                    json.dump(data, f, indent=4)
                
                st.success("Analysis completed!")

            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # Step 4: PDF Generation
        with st.container():
            st.write("### Step 4: Generating PDF report...")
            pdf_path = "reports/combined_report.pdf"
            
            with st.spinner("Creating PDF... Please wait."):
                create_combined_pdf("logos/logo.png", 'json/output.json')
            
            st.success("PDF generated successfully!")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with open(f"{pdf_path}", "rb") as pdf_file:
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_file,
                        file_name="evaluation_report.pdf",
                        mime="application/pdf",
                    )
    else:
        st.info("Please enter your name and upload a video file to start the analysis process.")

if __name__ == "__main__":
    main()
