import cv2
import time
import numpy as np
from load_models import face_model
from challenge_response import ChallengeResponder

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

class FaceVerifier:
    def __init__(self):

        self.CNN_CONF_THRESHOLD = 0.60
        self.prediction_buffer = []
        self.BUFFER_SIZE = 8

        self.challenge = ChallengeResponder()
        self.challenge_timeout = 7
        self.challenge_start_time = None

        self.MAX_CHALLENGE_ATTEMPTS = 2
        self.challenge_attempts = 0
        self.success_frame_counter = 0
        self.REQUIRED_SUCCESS_FRAMES = 10

        self.phase = 1
        self.system_start_time = time.time()

    def check_multiple_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 6)
        return len(faces)

    def predict_face(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 6)

        if len(faces) == 0:
            self.prediction_buffer.clear()
            return "NO_FACE", 0.0

        x, y, w, h = faces[0]
        face = frame[y:y+h, x:x+w]

        img = cv2.resize(face, (224, 224))
        img = img / 255.0
        img = np.expand_dims(img, axis=0)

        pred = face_model.predict(img, verbose=0)
        conf = float(pred[0][0])

        self.prediction_buffer.append(conf)
        if len(self.prediction_buffer) > self.BUFFER_SIZE:
            self.prediction_buffer.pop(0)

        avg_conf = np.mean(self.prediction_buffer)

        return ("Live" if avg_conf > self.CNN_CONF_THRESHOLD else "Spoof"), avg_conf

    def update(self, frame):

        # Global multiple face check
        num_faces = self.check_multiple_faces(frame)
        if num_faces > 1:
            self.prediction_buffer.clear()
            return "ONLY_ONE_PERSON_ALLOWED"

        if num_faces == 0 and self.phase != 1:
            return "PLEASE_FACE_CAMERA"

        if time.time() - self.system_start_time < 2:
            return "Initializing..."

        # ---------------- PHASE 1 ----------------
        if self.phase == 1:

            label, conf = self.predict_face(frame)

            if label == "NO_FACE":
                return "PLEASE_FACE_CAMERA"

            if label == "Spoof":
                return "FACE_SPOOFED"  # 🚨 STRICT BLOCK

            # Only LIVE moves to challenge
            self.phase = 2
            self.challenge_attempts = 0
            self.success_frame_counter = 0
            self.challenge.start_new_challenge()
            self.challenge_start_time = time.time()
            return "FACE_LIVE_CONFIRMED"

        # ---------------- PHASE 2 ----------------
        elif self.phase == 2:

            # Timeout check
            if time.time() - self.challenge_start_time > self.challenge_timeout:
                return self.handle_failure()

            status = self.challenge.update(frame)

            if status == "PASSED":
                self.success_frame_counter += 1
                if self.success_frame_counter >= self.REQUIRED_SUCCESS_FRAMES:
                    self.phase = 1
                    return "FACE_VERIFIED"
                return "CHALLENGE_ACTIVE"

            if status == "FAILED":
                return self.handle_failure()

            # If user stops action → decrease counter
            self.success_frame_counter = max(0, self.success_frame_counter - 1)
            return "CHALLENGE_ACTIVE"

    def handle_failure(self):
        self.success_frame_counter = 0
        self.challenge_attempts += 1

        if self.challenge_attempts < self.MAX_CHALLENGE_ATTEMPTS:
            self.challenge.start_new_challenge()
            self.challenge_start_time = time.time()
            return "RETRY_CHALLENGE"

        self.phase = 1
        return "FACE_CHALLENGE_FAILED"
    
    