import cv2
import numpy as np
import tempfile
import os
import tensorflow_hub as hub
import tensorflow as tf
from deepface import DeepFace
import json
class VideoAnalyzer:
    def __init__(self, video_file, speedup_factor=10):
        self.video_file = video_file
        self.speedup_factor = speedup_factor
        self.model = self.load_model()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        

        self.smile_count = 0
        self.previous_smile = False
        self.cooldown_frames = 0
        self.current_cooldown = 0

    def load_model(self):
        model_url = "https://tfhub.dev/google/movenet/singlepose/lightning/4"
        model = hub.load(model_url)
        return model.signatures['serving_default']

    def analyze_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_image = np.expand_dims(rgb_frame, axis=0)
        input_tensor = tf.convert_to_tensor(input_image, dtype=tf.int32)
        outputs = self.model(input_tensor)
        keypoints = outputs['output_0'].numpy()
        return self.process_keypoints(keypoints)

    def process_keypoints(self, keypoints):
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


    def detect_smiles(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        current_smile = False

        for (x, y, w, h) in faces:
            face_roi_gray = gray[y:y+h, x:x+w]
            face_height = face_roi_gray.shape[0]
            lower_face_roi = face_roi_gray[int(face_height*0.5):face_height, :]

            if self.current_cooldown <= 0:
                smiles = self.smile_cascade.detectMultiScale(
                    lower_face_roi,
                    scaleFactor=1.8,
                    minNeighbors=20,
                    minSize=(25, 25))
                current_smile = len(smiles) > 0

        # Handle cooldown
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            current_smile = False

        # Count smile transitions
        if not self.previous_smile and current_smile:
            self.smile_count += 1
            self.current_cooldown = self.cooldown_frames

        self.previous_smile = current_smile
        return self.smile_count

    def analyze_video(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_file.write(self.video_file.read())
            temp_video_path = temp_video_file.name

        cap = cv2.VideoCapture(temp_video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        self.cooldown_frames = int(1.5 * fps / self.speedup_factor)  # Adjusted cooldown
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        results = []
        

        energetic_start_frames = int(fps * 15)  
        positive_emotion_count = 0
        processed_start_frames = 0

        for frame_idx in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break


            if frame_idx % self.speedup_factor != 0:
                continue

    
            self.detect_smiles(frame)

            if frame_idx < energetic_start_frames:
                try:
                    emotions = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    if emotions[0]['dominant_emotion'] in ['happy', 'surprise']:
                        positive_emotion_count += 1
                    processed_start_frames += 1
                except:
                    pass

            if frame_idx % (int(fps * 2) * self.speedup_factor) == 0:
                resized_frame = cv2.resize(frame, (192, 192))
                result = self.analyze_frame(resized_frame)
                results.append(result)

        cap.release()
        os.remove(temp_video_path)

        posture_scores = [res["posture"] for res in results if "posture" in res]
        eye_contact_scores = [res["Eye Contact"] for res in results if "Eye Contact" in res]

        avg_posture = sum(posture_scores)/len(posture_scores) if posture_scores else 0
        avg_eye = sum(eye_contact_scores)/len(eye_contact_scores) if eye_contact_scores else 0
        
        video_duration = total_frames / fps
        smile_rate = self.smile_count / (video_duration / 60)  
        smile_score = min(5, (smile_rate / 5) * 5)

        energetic_score = 0
        if processed_start_frames > 0:
            positive_ratio = positive_emotion_count / processed_start_frames
            energetic_score = min(5, int(positive_ratio * 5)) 

        return {
            "posture": int(avg_posture),
            "Eye Contact": int(avg_eye),
            "Smile Score": int(smile_score),
            "Energetic Start": int((avg_posture + avg_eye + smile_score) / 3)
        }


