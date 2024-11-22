# Import the VideoAnalyzer class from video_analysis module
from posture_in_class import VideoAnalyzer

# Define the path to your video file
video_path = r'C:\Users\ayush\RE-LLM\myenv\compresseddhruv.mp4'  # Replace with your actual video path

# Create an instance of VideoAnalyzer and run the analysis
analyzer = VideoAnalyzer(video_path)
analyzer.analyze()  # This will print the average posture and eye contact scores
