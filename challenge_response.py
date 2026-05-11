
import cv2
import time
import random
import mediapipe as mp


class ChallengeResponder:
    def __init__(self):

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)

        self.instructions = [
            "Turn Left",
            "Turn Right",
            "Look Up",
            "Look Down"
        ]

        self.current_instruction = None
        self.start_time = None
        self.time_limit = 3.5  # Medium strict

        # Baseline pose
        self.base_yaw = None
        self.base_pitch = None

        # Medium strict thresholds
        self.TURN_THRESHOLD = 0.06
        self.LOOK_DOWN_THRESHOLD = 0.07
        self.LOOK_UP_THRESHOLD = 0.05

        # Stability requirement
        self.required_frames = 6
        self.pass_counter = 0

        # 🔥 IMPORTANT: Completion lock
        self.completed = False


    # -----------------------------------------
    # START NEW CHALLENGE
    # -----------------------------------------
    def start_new_challenge(self):

        self.current_instruction = random.choice(self.instructions)
        self.start_time = time.time()

        self.base_yaw = None
        self.base_pitch = None

        self.pass_counter = 0
        self.completed = False

        print("\nNew Challenge:", self.current_instruction)


    # -----------------------------------------
    # HEAD POSE DETECTION
    # -----------------------------------------
    def detect_head_pose(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        lm = results.multi_face_landmarks[0]

        nose = lm.landmark[1]
        left = lm.landmark[234]
        right = lm.landmark[454]
        forehead = lm.landmark[10]
        chin = lm.landmark[152]

        yaw = (nose.x - left.x) - (right.x - nose.x)
        pitch = (nose.y - forehead.y) - (chin.y - nose.y)

        return yaw, pitch


    # -----------------------------------------
    # UPDATE CHALLENGE STATE
    # -----------------------------------------
    def update(self, frame):

        # 🔒 If already completed, keep returning PASSED
        if self.completed:
            return "PASSED"

        # Timeout
        if time.time() - self.start_time > self.time_limit:
            print("Challenge TIMEOUT")
            return "FAILED"

        pose = self.detect_head_pose(frame)
        if pose is None:
            return "NO_FACE"

        yaw, pitch = pose

        # Lock baseline once
        if self.base_yaw is None:
            self.base_yaw = yaw
            self.base_pitch = pitch
            return "ONGOING"

        delta_yaw = yaw - self.base_yaw
        delta_pitch = pitch - self.base_pitch

        print(f"ΔYaw: {delta_yaw:.4f} | ΔPitch: {delta_pitch:.4f}")

        passed = False

        if self.current_instruction == "Turn Left" and delta_yaw > self.TURN_THRESHOLD:
            passed = True

        if self.current_instruction == "Turn Right" and delta_yaw < -self.TURN_THRESHOLD:
            passed = True

        if self.current_instruction == "Look Up" and delta_pitch < -self.LOOK_UP_THRESHOLD:
            passed = True

        if self.current_instruction == "Look Down" and delta_pitch > self.LOOK_DOWN_THRESHOLD:
            passed = True

        if passed:
            self.pass_counter += 1
            print("Stable frames:", self.pass_counter)

            if self.pass_counter >= self.required_frames:
                print(self.current_instruction, "PASSED")
                self.completed = True   # 🔥 Lock completion
                return "PASSED"
        else:
            self.pass_counter = 0

        return "ONGOING"