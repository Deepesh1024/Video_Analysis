import streamlit as st
import os
import json
from newtranscriber import VideoTranscriber
from ResumeEvaluator import VideoResumeEvaluator
from groqvision2 import VideoAnalyzer
from newpdfgen import PDFReportGenerator

# Set a custom theme
st.set_page_config(
    page_title="Video Analysis & Report Generator",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    output_json_path = "transcription_output.json"

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
    
    st.sidebar.image("logo.png", caption="School of Meaningful Experiences")
    
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
    
    # How to use section
    with st.expander("How to use this tool?", expanded=False):
        st.markdown("""
        1. Upload your video in one of the supported formats (MP4, MOV, AVI, MKV)
        2. The app will automatically:
           - Analyze the video content and presentation
           - Transcribe the speech to text
           - Evaluate the content using AI
           - Generate a comprehensive PDF report
        3. Download your PDF report to review the insights
        """)

    # File upload section
    uploaded_video = st.file_uploader("📤 **Upload a video file**", type=["mp4", "mov", "avi", "mkv"])
    
    if uploaded_video is not None:
        st.markdown("---")
        
        # Step 1: Video Analysis
        with st.container():
            st.write("### Step 1: Extracting insights from the video...")
            with st.spinner("Analyzing video... Please wait."):
                analyzer = VideoAnalyzer(uploaded_video)
                analyzer.analyze_video()
            st.success("Video analysis completed successfully!")
        
        # Step 2: Transcription
        transcription_output = process_video(uploaded_video)
        
        # Step 3: Evaluation
        with st.container():
            st.write("### Step 3: Evaluating transcription...")
            evaluator = VideoResumeEvaluator()
            with st.spinner("Evaluating content... Please wait."):
                output = evaluator.evaluate_transcription(transcription_output)
            
            try:
                # Process JSON files
                with open(r"transcription_output.json", "r") as f:
                    data = json.load(f)
                
                with open(r"output.json", 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                
                data['LLM'] = output
                
                with open(r"output.json", 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=4)
                
                st.success("Evaluation completed successfully!")
                
            except Exception as e:
                st.error(f"An error occurred during evaluation: {str(e)}")
                raise e
        
        # Step 4: PDF Generation
        with st.container():
            st.write("### Step 4: Generating PDF report...")
            json_path = r"output.json"
            pdf_path = "evaluation_report.pdf"
            
            with st.spinner("Creating PDF... Please wait."):
                pdf_generator = PDFReportGenerator(json_path, pdf_path)
                pdf_generator.create_pdf()
            
            st.success("PDF generated successfully!")
            
            # Download button with enhanced styling
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with open(r"evaluation_report.pdf", "rb") as pdf_file:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_file,
                        file_name="evaluation_report.pdf",
                        mime="application/pdf",
                    )
    else:
        st.info("👆 Please upload a video file to start the analysis process.")

if __name__ == "__main__":
    main()