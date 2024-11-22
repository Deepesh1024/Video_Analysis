import mediapipe as mp
import cv2
import numpy as np
import time
import math
import json

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

# Posture detection parameters
POSTURE_GOOD_ANGLE_RANGE = (68, 117)

# Eye contact parameters
SMOOTHING_WINDOW_SIZE = 10
EAR_THRESHOLD = 0.23
CONSECUTIVE_FRAMES_THRESHOLD = 3
Gaze_Variance_Weight = 0.60
Blink_Rate_Weight = 0.40
Blink_Rate_Penalty = 10

# Sentence segments (start_time, end_time) in seconds
sentence_segments = [
    (0, 4),  # Dear Ma'am, Sir, Thank you so much for having me here.
    (4, 9),  # I am Dhruv Gupta and I wish to apply into NTUS, PhD program for biomedical devices.
    (9, 12),  # I will begin with my academic journey.
    (12, 18),
    # My academic journey has been deeply rooted in exploring the intersection of engineering and health sector.
    (18, 24),  # I am pursuing a Bachelor of Science in Biology in the Indian Institute of Science, my glory.
    (24, 31),
    # I have consistently sought to blend learnings from biology and physiology with the passion for engineering and robotics.
    (31, 41),
    # During my time at IISE, I have taken courses in both these areas of interest and subjects which I have bridged it to.
    (41, 45),  # So for device making I have taken courses in operating systems and embedded systems.
    (45, 50),  # For biology I have taken courses in human physiology, medical neuroscience and neurobiology labs.
    (50, 59),
    # And as combination courses I have taken product manufacturing via medical devices, diagnostics and devices including neuroimaging.
    (59, 65),  # My interest in the health sector view gradually over a period of 3 years.
    (65, 73),
    # I in fact first got to know of the term medtech through an Estonian career accelerator which I joined remotely in my first semester at IISE.
    (73, 88),
    # I kept the concept in the term medtech in mind when I applied for a medical observorship at AIMS Delhi under the mentorship of Karnulal Dr. P.K. Sadhi, former neurologist to President MPG Abdul Kalam.
    (88, 96),
    # After acceptance I was encouraged to record high frequency problems happening at the hospital faced by patients.
    (96, 100),  # Hospital acquired infections made it to the top of the list.
    (100, 110),
    # At the time I was also interested in Nanda Parashat and that led me to found my startup Virokh with 3 co-founders and a team of 6.
    (110, 115),  # We received a seed funding of 10 lakhs or 1 million Indian rupees.
    (115, 120),  # We are currently building an MVP, a minimal viable product.
    (120, 131),
    # We have founded patents for free devices and are expecting to reduce the cost of our product to make it suitable for the Indian market.
    (131, 146),
    # After Virokh, me and part of my team decided to apply to the Indian Ministry of Defence for a summer project for helping soldiers with spinal cord injuries and rehabilitated them using a robotic gate trainer.
    (146, 150),  # I was approved by the Indian Chief of Army.
    (150, 158),  # Apart from my work has been facilitated by the entrepreneurship set of IISC and IEEE IISC.
    (158, 170),
    # As of February 2024, I am the student chair of CS Society of IEEE and Vice President of the Entrepreneurship set of IISC.
    (170, 180),
    # Leaning a team is mostly logistics. I sometimes prefer roles which allow me to focus on my developing and refining my skill set or sometimes a challenge.
    (180, 187),  # I am participating in a competition by IISC.
    (187, 199),
    # It is a vulnerable building competition which our team has cleared the first few rounds of and have received funding of 25 lakh rupees or 2.5 million Indian rupees
    (199, 204),  # to further our project.
    (204, 213),
    # Looking ahead, my goal is to continue leveraging my engineering acumen to drive effective and efficient solutions in the health tech sector.
    (213, 228),
    # My core strengths are leadership, innovation and a unique skill set of robotics, mettech devices and background in biology combined with acute market awareness.
    (228, 236),
    # I also wish to communicate that my personal mission is innovation of social impact. I want to help people with what I learned.
    (236, 244),  # Hence, I always seek to understand the application and implementation strategy of any idea first.
    (244, 250),  # IISC has founded an NGO, Devi Falhar, to distribute menstrual pads to slums in our city.
    (250, 257),
    # We soon figured out that it was not access to pads but rather perception of periods by the men in the house which is the main problem.
    (257, 262),  # And we switched to teaching young boys in the slum about period pain and menstrual health.
    (262, 267),  # We have some huge change there after in the feedback that we received from the women in the slums.
    (267, 277),
    # So, I would be most happy to work with projects where I get to work with people and understand why they are using my project and what they really, really need.
    (277, 281),  # Thank you so much for considering my application. It is an honour to be here.
    (281, 287),
    # I am eager to bring my perspective and skill set to NTU, Singapore and contribute to the esteemed institution.
    (287, 295)
    # I look forward to the opportunity to discuss how my background, skills and enthusiasm align with your PhD program. Thank you.
]


# Function to extract pose landmarks
def mediapipe_pose(frame):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(img_rgb)
    return result


# Function to compute posture score
def calculate_posture_score(keypoints, image_width, image_height):
    left_shoulder = np.array([keypoints.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * image_width,
                              keypoints.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * image_height])
    right_shoulder = np.array([keypoints.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * image_width,
                               keypoints.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * image_height])
    shoulder_midpoint = (left_shoulder + right_shoulder) / 2
    
    # Use EAR or NOSE to represent the head height
    head = np.array([keypoints.landmark[mp_pose.PoseLandmark.NOSE].x * image_width,
                     keypoints.landmark[mp_pose.PoseLandmark.NOSE].y * image_height])

    # Calculate the angle between the shoulder line and a vertical line
    shoulder_slope = (left_shoulder[1] - right_shoulder[1]) / (left_shoulder[0] - right_shoulder[0] + 1e-6)
    shoulder_angle = math.degrees(math.atan(shoulder_slope))
    
    # Check if posture is within good range
    if POSTURE_GOOD_ANGLE_RANGE[0] <= abs(shoulder_angle) <= POSTURE_GOOD_ANGLE_RANGE[1]:
        return 5  # Good posture
    else:
        return 1  # Bad posture



# Function to normalize landmark coordinates
def normalize_landmarks(landmarks, width, height):
    """Normalizes MediaPipe landmark coordinates by scaling them to the frame dimensions."""
    return [(int(landmark[0]), int(landmark[1])) for landmark in landmarks]


# Function to calculate Eye Aspect Ratio (EAR)
def calculate_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))


def eye_aspect_ratio(eye_points):
    vertical_1 = calculate_distance(eye_points[1], eye_points[5])
    vertical_2 = calculate_distance(eye_points[2], eye_points[4])
    horizontal = calculate_distance(eye_points[0], eye_points[3])
    return (vertical_1 + vertical_2) / (2.0 * horizontal)


# Function to detect pupil using adaptive thresholding
def detect_pupil(eye_image):
    gray_eye = cv2.cvtColor(eye_image, cv2.COLOR_BGR2GRAY)
    gray_eye = cv2.equalizeHist(gray_eye)
    gray_eye = cv2.GaussianBlur(gray_eye, (7, 7), 0)
    threshold_eye = cv2.adaptiveThreshold(gray_eye, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    contours, _ = cv2.findContours(threshold_eye, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

    if contours:
        (x, y, w, h) = cv2.boundingRect(contours[0])
        pupil_x = int(x + w / 2)
        pupil_y = int(y + h / 2)
        return pupil_x, pupil_y
    return None


# Function to apply stronger smoothing using a weighted moving average
def weighted_smooth_pupil_position(pupil_positions, new_position, window_size):
    pupil_positions.append(new_position)
    if len(pupil_positions) > window_size:
        pupil_positions.pop(0)

    if len(pupil_positions) == 0:
        return None

    weights = np.linspace(1, 0, len(pupil_positions))
    weights /= weights.sum()
    smoothed_position = np.average(pupil_positions, axis=0, weights=weights).astype(int)
    return smoothed_position


# Function to calculate the smoothed gaze point
def smooth_gaze_point(gaze_points, new_gaze_point, window_size):
    gaze_points.append(new_gaze_point)
    if len(gaze_points) > window_size:
        gaze_points.pop(0)

    if len(gaze_points) == 0:
        return None

    smoothed_gaze = np.mean(gaze_points, axis=0).astype(int)
    return smoothed_gaze


# Function to calculate gaze variance
def calculate_gaze_variance(gaze_directions):
    if len(gaze_directions) < 2:
        return 0
    points = np.array(gaze_directions)
    mean_point = np.mean(points, axis=0)
    variance = np.mean(np.sum((points - mean_point) ** 2, axis=1))
    return variance


# Process video for posture and eye contact score for each segment
def process_video_segment(video_path, segment_start, segment_end):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, segment_start * 1000)

    blink_count = 0
    gaze_directions = []
    consecutive_frames = 0
    eye_closed = False
    good_posture_count = 0
    total_posture_count = 0
    start_time = time.time()
    pupil_positions_left = []
    pupil_positions_right = []

    while cap.isOpened():
        ret, frame = cap.read()
        current_time_in_video = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

        if not ret or current_time_in_video > segment_end:
            break

        image_height, image_width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark

                # Extract the left and right eye landmarks (landmark indices same as before)
                left_eye_landmarks = np.array([(landmarks[i].x * image_width, landmarks[i].y * image_height)
                                               for i in [33, 160, 158, 133, 153, 144]])
                right_eye_landmarks = np.array([(landmarks[i].x * image_width, landmarks[i].y * image_height)
                                                for i in [362, 385, 387, 263, 373, 380]])

                # Normalize landmarks
                left_eye = normalize_landmarks(left_eye_landmarks, image_width, image_height)
                right_eye = normalize_landmarks(right_eye_landmarks, image_width, image_height)

                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)
                avg_ear = (left_ear + right_ear) / 2.0

                # Detect pupils
                left_eye_roi = frame[int(left_eye_landmarks[:, 1].min()):int(left_eye_landmarks[:, 1].max()),
                               int(left_eye_landmarks[:, 0].min()):int(left_eye_landmarks[:, 0].max())]
                right_eye_roi = frame[int(right_eye_landmarks[:, 1].min()):int(right_eye_landmarks[:, 1].max()),
                                int(right_eye_landmarks[:, 0].min()):int(right_eye_landmarks[:, 0].max())]

                left_pupil = detect_pupil(left_eye_roi)
                right_pupil = detect_pupil(right_eye_roi)

                smoothed_left_pupil = weighted_smooth_pupil_position(pupil_positions_left, left_pupil,
                                                                     SMOOTHING_WINDOW_SIZE) if left_pupil else None
                smoothed_right_pupil = weighted_smooth_pupil_position(pupil_positions_right, right_pupil,
                                                                      SMOOTHING_WINDOW_SIZE) if right_pupil else None

                if smoothed_left_pupil.any() and smoothed_right_pupil.any():
                    gaze_point = ((smoothed_left_pupil[0] + smoothed_right_pupil[0]) // 2,
                                  (smoothed_left_pupil[1] + smoothed_right_pupil[1]) // 2)
                    smoothed_gaze_point = smooth_gaze_point(gaze_directions, gaze_point, SMOOTHING_WINDOW_SIZE)
                    if smoothed_gaze_point.any():
                        gaze_directions.append(smoothed_gaze_point)

                # Blink detection logic
                if avg_ear < EAR_THRESHOLD:
                    consecutive_frames += 1
                    if consecutive_frames >= CONSECUTIVE_FRAMES_THRESHOLD and not eye_closed:
                        blink_count += 1
                        eye_closed = True
                else:
                    consecutive_frames = 0
                    eye_closed = False
        # Detect posture using pose landmarks
        pose_result = mediapipe_pose(frame)
        if pose_result.pose_landmarks:
            total_posture_count += 1
            posture_score = calculate_posture_score(pose_result.pose_landmarks, image_width, image_height)
            good_posture_count += (posture_score == 5)

    cap.release()
    # Calculate blink rate and gaze variance
    elapsed_time = time.time() - start_time
    blink_rate = blink_count / elapsed_time if elapsed_time > 0 else 0
    gaze_variance = calculate_gaze_variance(gaze_directions)

    # Compute confidence score
    eye_contact_score = max(0, 5 - (gaze_variance * Gaze_Variance_Weight + blink_rate * Blink_Rate_Penalty))
    eye_contact_score = min(int(round(eye_contact_score)), 5)

    posture_score = int(good_posture_count / total_posture_count * 5) if total_posture_count > 0 else 1

    return eye_contact_score, posture_score


# Process video for all segments
video_path = r"C:\Users\ayush\RE-LLM\myenv\compresseddhruv.mp4"

eye_scores = []
p_scores = []
for segment_start, segment_end in sentence_segments:
    eye_contact_score, posture_score = process_video_segment(video_path, segment_start, segment_end)
    print(
        f"Segment ({segment_start}s to {segment_end}s) - Eye Contact Score: {eye_contact_score}, Posture Score: {posture_score}")
    eye_scores.append(eye_contact_score)
    p_scores.append(posture_score)

if len(eye_scores) > 10:
    eye_scores.sort()
    eye_scores_to_average = eye_scores[10:]
    p_scores.sort()
    p_scores_to_average = p_scores[10:]
else:
    eye_scores_to_average = eye_scores
    p_scores_to_average = p_scores

eye_average_score = sum(eye_scores_to_average) / len(eye_scores_to_average)
p_average_score = sum(p_scores_to_average) / len(p_scores_to_average)

COMMENTS = {1: "Needs Improvement",
            2: "Poor",
            3: "Satisfactory",
            4: "Good",
            5: "Excellent"}
print("Eye contact comment:", COMMENTS[(int(eye_average_score))])


print("Posture comment:", COMMENTS[(int(p_average_score))])

output_json_path = r"C:\Users\ayush\RE-LLM\myenv\output.json"
ps = f"Eye contact comment:, {COMMENTS[(int(eye_average_score))]}"
ec = f"Posture comment:{COMMENTS[(int(p_average_score))]}"
output_data = {"Eye contact comment:" : COMMENTS[(int(eye_average_score))] ,"Posture Comment : " : COMMENTS[(int(p_average_score))]}

def save_to_json(filename):
    with open(filename, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

save_to_json(output_json_path)
