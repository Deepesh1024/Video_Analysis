import cv2
import numpy as np
import tempfile
import os
import streamlit as st
import tensorflow_hub as hub
import json 
import tensorflow as tf

class VideoAnalyzer:
    def __init__(self, video_file):
        self.video_file = video_file
        self.model = self.load_model()

    def load_model(self):
        # Load the PoseNet model from TensorFlow Hub
        model_url = "https://tfhub.dev/google/movenet/singlepose/lightning/4"  # PoseNet URL
        model = hub.load(model_url)
        return model.signatures['serving_default']  # This allows you to call the model with the correct signature

    def analyze_frame(self, frame):
        # Convert the frame to RGB (PoseNet works with RGB images)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_image = np.expand_dims(rgb_frame, axis=0)  # Add batch dimension

        # Convert to TensorFlow tensor with the correct dtype
        input_tensor = tf.convert_to_tensor(input_image, dtype=tf.int32)

        # Run the frame through the model (use the correct function from the signature)
        outputs = self.model(input_tensor)

        # Extract keypoints from the output dictionary (the keypoints are in the 'output_0' field)
        keypoints = outputs['output_0'].numpy()

        return self.process_keypoints(keypoints)

    def process_keypoints(self, keypoints):
        # Extract body posture score based on keypoints (e.g., distance between body parts)
        posture_score = self.calculate_posture_score(keypoints)
        eye_contact_score = self.calculate_eye_contact_score(keypoints)

        return {"posture": posture_score, "Eye Contact": eye_contact_score}

    def calculate_posture_score(self, keypoints):
        # Placeholder: Calculate the posture score based on the head-shoulder distance
        head_x, head_y, head_conf = keypoints[0][0][0]
        shoulder_x, shoulder_y, shoulder_conf = keypoints[0][0][5]  # Right shoulder keypoint (index 5)
        
        distance = np.sqrt((head_x - shoulder_x) ** 2 + (head_y - shoulder_y) ** 2)
        posture_score = min(distance * 10, 10)  # Example scaling
        
        return posture_score

    def calculate_eye_contact_score(self, keypoints):
        # Assuming that keypoints[0][0][1] and keypoints[0][0][2] represent the left and right eyes
        left_eye_x, left_eye_y, left_eye_conf = keypoints[0][0][1]  # Left eye keypoint (index 1)
        right_eye_x, right_eye_y, right_eye_conf = keypoints[0][0][2]  # Right eye keypoint (index 2)
        
        # Assuming that keypoints[0][0][0] represents the head center (the nose)
        head_x, head_y, head_conf = keypoints[0][0][0]  # Nose or head center keypoint (index 0)

        if left_eye_conf > 0.5 and right_eye_conf > 0.5:  # If both eyes are detected with high confidence
            left_diff = abs(left_eye_x - head_x)
            right_diff = abs(right_eye_x - head_x)
            
            eye_contact_score = max(5 - (left_diff + right_diff), 0)  # Normalize score between 0 and 10
        else:
            eye_contact_score = 0

        return eye_contact_score

    def analyze_video(self):
        # Create a temporary file to save the uploaded video
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_file.write(self.video_file.read())  # Write uploaded video to the temporary file
            temp_video_path = temp_video_file.name  # Get the path of the temporary file
        
        # Open the video with OpenCV (now that we have a file path)
        cap = cv2.VideoCapture(temp_video_path)
        results = []

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * 2)  # Process every 2 seconds of video
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_interval != 0:
                continue

            frame = cv2.resize(frame, (192, 192))  # Resize frame for analysis

            result = self.analyze_frame(frame)
            if result:
                results.append(result)

        cap.release()
        
        # Remove the temporary video file after processing
        os.remove(temp_video_path)

        # Process and return feedback
        posture_scores = [res["posture"] for res in results if "posture" in res]
        eye_contact_scores = [res["Eye Contact"] for res in results if "Eye Contact" in res]

        avg_posture_score = sum(posture_scores) / len(posture_scores) if posture_scores else 0
        avg_eye_contact_score = sum(eye_contact_scores) / len(eye_contact_scores) if eye_contact_scores else 0

        feedback = {
            "posture": int(avg_posture_score),
            "Eye Contact": int(avg_eye_contact_score)
        }

        with open("output.json", 'w', encoding='utf-8') as json_file:
            json.dump(feedback, json_file, ensure_ascii=False, indent=4)

        return feedback

# Streamlit interface
# uploaded_video = st.file_uploader("Choose a video...", type=["mp4", "mov", "avi", "mkv"])

# if uploaded_video is not None:
#     st.write("Extracting Video Data")
#     analyzer = VideoAnalyzer(uploaded_video)
#     feedback = analyzer.analyze_video()  # Process the uploaded video
#     st.write(feedback)  # Display feedback after processing
