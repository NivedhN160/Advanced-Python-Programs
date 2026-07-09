import cv2
import time
import json
import math
import argparse
import numpy as np
import mediapipe as mp
from deepface import DeepFace

FRUSTRATION_THRESHOLD = 0.6
BLINK_EAR_THRESHOLD = 0.19
BLINK_CONSEC_FRAMES = 2
LOG_FILE = "frustration_log.json"
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
LEFT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]

def eye_aspect_ratio(pts):
    A = math.dist(pts[1], pts[5])
    B = math.dist(pts[2], pts[4])
    C = math.dist(pts[0], pts[3])
    ear = (A + B) / (2.0 * C)
    return ear

def get_blink_and_headpose_and_distance(face_landmarks, image_w, image_h):
    mesh_points = np.array(
        [(int(p.x * image_w), int(p.y * image_h), p.z) for p in face_landmarks.landmark]
    )

    left_eye_pts = [(mesh_points[i][0], mesh_points[i][1]) for i in LEFT_EYE_LANDMARKS]
    right_eye_pts = [(mesh_points[i][0], mesh_points[i][1]) for i in RIGHT_EYE_LANDMARKS]

    left_ear = eye_aspect_ratio(left_eye_pts)
    right_ear = eye_aspect_ratio(right_eye_pts)
    ear = (left_ear + right_ear) / 2.0

    nose = mesh_points[1]
    chin = mesh_points[152]
    head_tilt = math.degrees(math.atan2(chin[1] - nose[1], chin[0] - nose[0]))

    dist_face = math.dist((nose[0], nose[1]), (chin[0], chin[1]))

    return ear, head_tilt, dist_face

def get_emotion(frame, face_box):
    x, y, w, h = face_box
    x, y = max(0, x), max(0, y)
    roi = frame[y:y+h, x:x+w]
    if roi.size == 0 or w == 0 or h == 0:
        return "neutral", 0.0
    try:
        # silent=True prevents DeepFace from printing to stdout constantly
        result = DeepFace.analyze(
            roi,
            actions=['emotion'],
            enforce_detection=False,
            silent=True
        )
        res0 = result[0] if isinstance(result, list) else result
        dominant = res0['dominant_emotion']
        score = res0['emotion'][dominant] / 100.0
        return dominant, score
    except Exception:
        return "neutral", 0.0

def map_features_to_frustration(emotion, emotion_score, blink_rate, head_tilt, face_size_norm):
    score = 0.0

    # emotions
    if emotion in ["angry", "sad", "fear", "disgust"]:
        score += 0.4 * emotion_score
    elif emotion == "happy":
        score -= 0.2 * emotion_score

    if blink_rate > 25:
        score += 0.2
    elif blink_rate < 5:
        score += 0.1

    if abs(head_tilt) > 20:
        score += 0.1

    if face_size_norm > 0.12:
        score += 0.2

    return max(0.0, min(1.0, score))

def load_log():
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_log(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def detect_basic_sign(hand_landmarks):
    """Simple heuristics to detect common hand signs based on finger extension."""
    tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    pips = [
        mp_hands.HandLandmark.INDEX_FINGER_PIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp_hands.HandLandmark.RING_FINGER_PIP,
        mp_hands.HandLandmark.PINKY_PIP
    ]
    
    # Check if fingers are extended (tip is higher than PIP joint, y goes down)
    fingers_up = []
    for tip, pip in zip(tips, pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers_up.append(True)
        else:
            fingers_up.append(False)
            
    # Thumb: check if it's pointing up or down relative to its IP joint
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    
    thumb_up = thumb_tip.y < (thumb_ip.y - 0.02)
    thumb_down = thumb_tip.y > (thumb_ip.y + 0.02)
    
    if all(fingers_up):
        return "Open Hand"
    elif fingers_up == [True, True, False, False]:
        return "Peace Sign"
    elif fingers_up == [False, False, False, False]:
        if thumb_up:
            return "Thumbs Up"
        elif thumb_down:
            return "Thumbs Down"
        else:
            return "Fist"
    elif fingers_up == [True, False, False, False]:
        return "Pointing Index"
        
    return "Unknown Sign"

class FaceTracker:
    def __init__(self):
        self.faces = {} # id -> state dictionary
        self.next_id = 0
        
    def update(self, current_faces_data):
        """
        Takes current frame's detected faces and matches them to tracked faces.
        Returns the data with assigned IDs.
        """
        new_faces = {}
        matched_ids = set()
        
        for face_data in current_faces_data:
            cx, cy = face_data['center']
            
            # Find the closest existing face
            best_id = None
            min_dist = float('inf')
            
            for fid, state in self.faces.items():
                if fid in matched_ids: 
                    continue
                px, py = state['center']
                dist = math.dist((cx, cy), (px, py))
                
                # Threshold to consider it the same face (in pixels)
                if dist < 150: 
                    if dist < min_dist:
                        min_dist = dist
                        best_id = fid
            
            if best_id is not None:
                # Update existing tracked face
                state = self.faces[best_id]
                state['center'] = (cx, cy)
                new_faces[best_id] = state
                matched_ids.add(best_id)
                face_data['id'] = best_id
            else:
                # Assign new ID to new face
                now = time.time()
                new_id = self.next_id
                new_faces[new_id] = {
                    'center': (cx, cy),
                    'blink_counter': 0,
                    'consec_closed': 0,
                    'start_time': now,
                    'last_minute_time': now,
                    'blinks_last_minute': 0,
                    'blink_rate': 0,
                    'emotion': 'neutral',
                    'emotion_score': 0.0,
                    'last_emotion_time': 0 # to throttle DeepFace calls
                }
                self.next_id += 1
                face_data['id'] = new_id
                
        self.faces = new_faces
        return current_faces_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Current code file name", default="unknown_file.py")
    args = parser.parse_args()
    file_name = args.file

    cap = cv2.VideoCapture(0)
    
    # Request a higher resolution from the webcam
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Create a resizable window and set it to a large default size
    cv2.namedWindow("Emotion-Aware Debugging Assistant", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Emotion-Aware Debugging Assistant", 1280, 720)

    log_data = load_log()
    if file_name not in log_data:
        log_data[file_name] = []

    tracker = FaceTracker()

    with mp_face_mesh.FaceMesh(
        max_num_faces=10, 
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh, mp_hands.Hands(
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
        max_num_hands=2
    ) as hands_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process faces and hands
            results = face_mesh.process(rgb)
            hands_results = hands_mesh.process(rgb)

            current_faces_data = []

            # Extract basic bounding box and center for each face detected by Mediapipe
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    xs = [int(p.x * w) for p in face_landmarks.landmark]
                    ys = [int(p.y * h) for p in face_landmarks.landmark]
                    
                    # Compute tight bounding box
                    x_min_tight = max(min(xs), 0)
                    x_max_tight = min(max(xs), w-1)
                    y_min_tight = max(min(ys), 0)
                    y_max_tight = min(max(ys), h-1)
                    
                    # Add a 20% margin to the bounding box so DeepFace gets better context
                    w_tight = x_max_tight - x_min_tight
                    h_tight = y_max_tight - y_min_tight
                    margin_x = int(w_tight * 0.2)
                    margin_y = int(h_tight * 0.2)
                    
                    x_min = max(0, x_min_tight - margin_x)
                    y_min = max(0, y_min_tight - margin_y)
                    x_max = min(w - 1, x_max_tight + margin_x)
                    y_max = min(h - 1, y_max_tight + margin_y)
                    
                    face_box = (x_min, y_min, x_max - x_min, y_max - y_min)
                    
                    cx = x_min_tight + w_tight // 2
                    cy = y_min_tight + h_tight // 2
                    
                    current_faces_data.append({
                        'center': (cx, cy),
                        'landmarks': face_landmarks,
                        'box': face_box
                    })

            # Update tracker and retrieve faces with IDs
            tracked_faces = tracker.update(current_faces_data)
            
            # Display overall face count on top left with a distinct color (Cyan in BGR)
            cv2.putText(frame, f"Faces detected: {len(tracked_faces)}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            now = time.time()
            for face_data in tracked_faces:
                fid = face_data['id']
                face_landmarks = face_data['landmarks']
                face_box = face_data['box']
                x_min, y_min, w_box, h_box = face_box
                x_max = x_min + w_box
                y_max = y_min + h_box
                
                state = tracker.faces[fid]
                
                ear, head_tilt, face_size = get_blink_and_headpose_and_distance(face_landmarks, w, h)

                # Process Blinking
                if ear < BLINK_EAR_THRESHOLD:
                    state['consec_closed'] += 1
                else:
                    if state['consec_closed'] >= BLINK_CONSEC_FRAMES:
                        state['blink_counter'] += 1
                        state['blinks_last_minute'] += 1
                    state['consec_closed'] = 0

                # Blink rate per minute
                if now - state['last_minute_time'] >= 60:
                    state['blink_rate'] = state['blinks_last_minute'] / ((now - state['last_minute_time']) / 60.0)
                    state['last_minute_time'] = now
                    state['blinks_last_minute'] = 0

                # Throttle DeepFace emotion analysis to avoid lag (e.g., once every 0.5 seconds)
                if now - state['last_emotion_time'] > 0.5:
                    emotion, emo_score = get_emotion(frame, face_box)
                    state['emotion'] = emotion
                    state['emotion_score'] = emo_score
                    state['last_emotion_time'] = now
                else:
                    emotion = state['emotion']
                    emo_score = state['emotion_score']

                face_size_norm = (w_box * h_box) / float(w * h + 1e-6)

                frustration_score = map_features_to_frustration(
                    emotion, emo_score, state['blink_rate'], head_tilt, face_size_norm
                )

                # Draw per-face overlay
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {fid} | {emotion}",
                            (x_min, max(0, y_min - 40)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                cv2.putText(frame, f"EAR: {ear:.2f} | Blinks/m: {state['blink_rate']:.1f}",
                            (x_min, max(0, y_min - 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                cv2.putText(frame, f"Frus: {frustration_score:.2f}",
                            (x_min, max(0, y_min - 60)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # trigger "help" if frustration high (drawn below the face)
                if frustration_score > FRUSTRATION_THRESHOLD:
                    cv2.putText(frame, "SUGGEST BREAK",
                                (x_min, min(h-10, y_max + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Log every 5 seconds per face
                if now - state['start_time'] > 5:
                    log_data[file_name].append({
                        "face_id": fid,
                        "timestamp": now,
                        "emotion": emotion,
                        "frustration": float(frustration_score),
                        "blink_rate": float(state['blink_rate']),
                        "head_tilt": float(head_tilt),
                        "face_size_norm": float(face_size_norm)
                    })
                    save_log(log_data)
                    state['start_time'] = now
            
            # Process Hand Gestures / Sign Language
            if hands_results.multi_hand_landmarks:
                for i, hand_landmarks in enumerate(hands_results.multi_hand_landmarks):
                    # Draw landmarks on hands
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Detect basic sign language gesture
                    sign = detect_basic_sign(hand_landmarks)
                    
                    # Get top-left coordinate of the hand to display text
                    hx = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * w)
                    hy = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * h)
                    
                    cv2.putText(frame, f"Sign: {sign}", (hx, hy + 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 100, 255), 2)
                                
            cv2.imshow("Emotion-Aware Debugging Assistant", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
