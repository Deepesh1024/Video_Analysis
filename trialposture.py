import cv2
import mediapipe as mp
import numpy as np
import json
import math

# Class for posture and eye contact scoring
class PostureEyeScorer:
    def __init__(self, video_path):
        self.video_path = video_path
        # Use lower complexity for better performance
        self.pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=0, enable_segmentation=False)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(max_num_faces=1)

    # Calculate posture score based on how long the person is sitting straight
    def calculate_posture_score(self, landmarks, time_sitting_straight):
        left_shoulder = np.array([landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                  landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y])
        right_shoulder = np.array([landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                   landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].y])
        head = np.array([landmarks[mp.solutions.pose.PoseLandmark.NOSE.value].x,
                         landmarks[mp.solutions.pose.PoseLandmark.NOSE.value].y])

        shoulder_vector = right_shoulder - left_shoulder
        head_vector = head - np.mean([left_shoulder, right_shoulder], axis=0)

        # Calculate angle between head and shoulder vectors
        dot_product = np.dot(shoulder_vector, head_vector)
        norm_product = np.linalg.norm(shoulder_vector) * np.linalg.norm(head_vector)

        if norm_product == 0:
            return 0  # Avoid division by zero

        cos_angle = dot_product / norm_product
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angle = math.degrees(math.acos(cos_angle))

        # Determine the score based on how straight the posture is and time sitting straight
        score = max(0, min(5, 5 - (angle / 10)))  # Scale the score to 5
        # Add time sitting straight to influence the score (e.g., each second adds to the score)
        time_influence = min(time_sitting_straight / 10, 5 - score)  # Ensure we don't exceed the cap
        total_score = max(0, min(5, score + time_influence))  # Capped at 5
        return total_score

    def calculate_eye_contact_score(self, landmarks, time_looking_center):
        face_center = np.mean(np.array([[landmarks[10].x, landmarks[10].y], [landmarks[152].x, landmarks[152].y]]), axis=0)
        screen_center = np.array([0.5, 0.5])  

        distance_to_center = np.linalg.norm(face_center - screen_center)
        score = max(0, (1 - distance_to_center) * 5) + time_looking_center / 10  # Scale the score to 5
        return max(0, min(5, score))  # Ensure score does not exceed 5

    # Process the video and compute average posture and eye contact scores
    def process_video(self):
        cap = cv2.VideoCapture(self.video_path)

        posture_scores = []
        eye_contact_scores = []

        frame_count = 0
        frame_skip = 5  # Skip frames to reduce processing
        time_sitting_straight = 0
        time_looking_center = 0

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (640, 480))  # Resize for efficiency

            # Pose estimation
            pose_results = self.pose.process(frame_resized)
            if pose_results.pose_landmarks:
                landmarks = pose_results.pose_landmarks.landmark
                # Increment time based on posture detection logic
                if landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y < landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].y and \
                   landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].y < landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value].y:
                    time_sitting_straight += 1  # Increment time if sitting straight
                
                posture_scores.append(self.calculate_posture_score(landmarks, time_sitting_straight))

            # Face mesh (eye contact) estimation
            face_mesh_results = self.face_mesh.process(frame_resized)
            if face_mesh_results.multi_face_landmarks:
                for face_landmarks in face_mesh_results.multi_face_landmarks:
                    # Check if looking at the center of the screen (distance less than a threshold)
                    distance_to_center = self.calculate_eye_contact_score(face_landmarks.landmark, time_looking_center)
                    if distance_to_center < 0.1:  # Arbitrary threshold for looking at the center
                        time_looking_center += 1  # Increment time looking at center
                    eye_contact_scores.append(self.calculate_eye_contact_score(face_landmarks.landmark, time_looking_center))

        cap.release()
        self.pose.close()
        self.face_mesh.close()

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

        feedback = {
            "Eye": "Excellent" if avg_eye_contact_score >= 4.7 else "Good" if avg_eye_contact_score > 4.2 else "Satisfactory" if avg_eye_contact_score > 3 else "Poor" if avg_eye_contact_score > 2.5 else "Needs Improvement",
            "Posture": "Excellent" if avg_posture_score >= 4.7 else "Good" if avg_posture_score > 4.2 else "Satisfactory" if avg_posture_score > 3 else "Poor" if avg_posture_score > 2.5 else "Needs Improvement"
        }

        with open(r"C:\Users\ayush\RE-LLM\myenv\output.json", 'w', encoding='utf-8') as json_file:
            json.dump(feedback, json_file, ensure_ascii=False, indent=4)

# Example usage
if __name__ == "__main__":
    video_path = r'C:\Users\ayush\RE-LLM\myenv\dhruvresume.mp4'  # Replace with your video file path
    analyzer = VideoAnalyzer(video_path)
    analyzer.analyze()
