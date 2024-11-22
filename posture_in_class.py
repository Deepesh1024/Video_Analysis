import cv2
import mediapipe as mp
import numpy as np
import json
import math
# Class for posture and eye contact scoring
class PostureEyeScorer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(max_num_faces=1)

    def calculate_posture_score(self, landmarks):
        left_shoulder = np.array([landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].x,
                              landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y])
        right_shoulder = np.array([landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                               landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].y])
        left_hip = np.array([landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].x,
                         landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].y])
        right_hip = np.array([landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value].x,
                          landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value].y])
        shoulder_vector = right_shoulder - left_shoulder
        hip_vector = right_hip - left_hip
        dot_product = np.dot(shoulder_vector, hip_vector)
        norm_product = np.linalg.norm(shoulder_vector) * np.linalg.norm(hip_vector)
        if norm_product == 0:
            return 0  
        cos_angle = dot_product / norm_product
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angle = math.degrees(math.acos(cos_angle))
        score = max(0, min(5, 5 - (angle / 10)))  
        return score


    # Calculate eye contact score (scaled to 5) based on face landmarks
    def calculate_eye_contact_score(self, landmarks):
        left_eye_center = np.mean(np.array([[landmarks[133].x, landmarks[133].y], [landmarks[33].x, landmarks[33].y]]), axis=0)
        right_eye_center = np.mean(np.array([[landmarks[362].x, landmarks[362].y], [landmarks[263].x, landmarks[263].y]]), axis=0)
        face_center = np.mean(np.array([[landmarks[10].x, landmarks[10].y], [landmarks[152].x, landmarks[152].y]]), axis=0)
        eye_to_center_distance = np.linalg.norm(left_eye_center - face_center) + np.linalg.norm(right_eye_center - face_center)

        score = 1 - eye_to_center_distance
        return max(0, min(1, score)) * 5  
    def process_video(self):
        cap = cv2.VideoCapture(self.video_path)

        posture_scores = []
        eye_contact_scores = []

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Pose estimation
            pose_results = self.pose.process(frame_rgb)
            if pose_results.pose_landmarks:
                landmarks = pose_results.pose_landmarks.landmark
                posture_scores.append(self.calculate_posture_score(landmarks))

            # Face mesh (eye contact) estimation
            face_mesh_results = self.face_mesh.process(frame_rgb)
            if face_mesh_results.multi_face_landmarks:
                for face_landmarks in face_mesh_results.multi_face_landmarks:
                    eye_contact_scores.append(self.calculate_eye_contact_score(face_landmarks.landmark))

        cap.release()

        # Calculate average scores
        avg_posture_score = np.mean(posture_scores) if posture_scores else 0
        avg_eye_contact_score = np.mean(eye_contact_scores) if eye_contact_scores else 0

        return avg_posture_score, avg_eye_contact_score

class VideoAnalyzer:
    def __init__(self, video_path):
        self.scorer = PostureEyeScorer(video_path)

    # Run analysis and print the results
    def analyze(self):
        avg_posture_score, avg_eye_contact_score = self.scorer.process_video()

        print(f'Average Posture Score (out of 5): {avg_posture_score:.2f}')
        print(f'Average Eye Contact Score (out of 5): {avg_eye_contact_score:.2f}')
        eyecomm = ""
        postcomm = ""

        if avg_eye_contact_score > 4 : eyecomm = "Excellent"
        elif avg_eye_contact_score > 3 : eyecom = "Good"
        elif avg_eye_contact_score > 2 : eyecom = "Satisfactory"
        else : eyecom = "Poor"
        
        if avg_posture_score > 4 : postcomm = "Excellent"
        elif avg_posture_score > 3 : postcomm = "Good"
        elif avg_posture_score > 2 : postcomm = "Satisfactory"
        else : postcomm = "Poor"
        
        with open(r"C:\Users\ayush\RE-LLM\myenv\output.json", 'w', encoding='utf-8') as json_file:
            json.dump({"Eye" :  eyecomm , "Posture" : postcomm}, json_file, ensure_ascii=False, indent=4)
            
            

# Example usage
if __name__ == "__main__":
    video_path = r'C:\Users\ayush\RE-LLM\myenv\compresseddhruv.mp4'  # Replace with your video file path
    analyzer = VideoAnalyzer(video_path)
    analyzer.analyze()
