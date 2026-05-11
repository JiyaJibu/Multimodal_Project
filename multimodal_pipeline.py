# # import cv2
# # import numpy as np
# # from load_models import fingerprint_model
# # from capture_fingerprint import capture_fingerprint


# # # ---------------------------
# # # FINGERPRINT PREPROCESS
# # # ---------------------------
# # def preprocess_fingerprint(img):

# #     if img is None:
# #         return None

# #     if len(img.shape) == 2:
# #         img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

# #     img = cv2.resize(img, (224, 224))
# #     img = img / 255.0
# #     img = np.expand_dims(img, axis=0)

# #     return img


# # # ---------------------------
# # # FINGERPRINT PREDICTION
# # # ---------------------------
# # def predict_fingerprint():

# #     img = capture_fingerprint()

# #     # Hardware fake detection
# #     if isinstance(img, str) and img == "FAKE_HARDWARE":
# #         return "Spoof", 0.0

# #     if img is None:
# #         return "Spoof", 0.0

# #     img_processed = preprocess_fingerprint(img)

# #     pred = fingerprint_model.predict(img_processed, verbose=0)[0]
# #     conf = float(np.squeeze(pred))

# #     THRESHOLD = 0.80   # Stronger security threshold

# #     if conf >= THRESHOLD:
# #         return "Live", conf
# #     else:
# #         return "Spoof", conf


# # # ---------------------------
# # # SCORE FUSION (Optional)
# # # ---------------------------
# # def fuse_scores(face_conf, fp_conf,
# #                 face_weight=0.4,
# #                 fp_weight=0.6):

# #     return face_conf * face_weight + fp_conf * fp_weight











# import cv2
# import numpy as np
# from load_models import fingerprint_model
# from face_pipeline import run_face_pipeline
# from capture_fingerprint import capture_fingerprint


# # ---------------------------
# # FINGERPRINT PREPROCESS
# # ---------------------------
# def preprocess_fingerprint(img):
#     if img is None:
#         return None

#     if len(img.shape) == 2:
#         img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

#     img = cv2.resize(img, (224, 224))
#     img = img / 255.0
#     img = np.expand_dims(img, axis=0)

#     return img


# # ---------------------------
# # FINGERPRINT PREDICTION
# # ---------------------------
# def predict_fingerprint():

#     img = capture_fingerprint()

#     # Hardware fake detection
#     if isinstance(img, str) and img == "FAKE_HARDWARE":
#         return "Spoof", 0.0

#     if img is None:
#         return "NoFingerprint", 0.0

#     img_processed = preprocess_fingerprint(img)

#     pred = fingerprint_model.predict(img_processed, verbose=0)[0]
#     conf = float(np.squeeze(pred))

#     if conf > 0.65:
#         return "Live", conf
#     else:
#         return "Spoof", conf


# # ---------------------------
# # MAIN MULTIMODAL FLOW
# # ---------------------------
# def run_multimodal_verification():

#     print("\n🔹 Starting Multimodal Verification")

#     # 1️⃣ Face Verification
#     face_result = run_face_pipeline()

#     if face_result != "Live":
#         print("❌ ACCESS DENIED — Face Spoof")
#         return "Denied"

#     print("✅ Face Verified. Scan Fingerprint...")

#     # 2️⃣ Fingerprint Verification
#     fp_label, fp_conf = predict_fingerprint()

#     print(f"Fingerprint: {fp_label} (Confidence: {fp_conf:.4f})")

#     if fp_label == "Live":
#         print("✅ ACCESS GRANTED")
#         return "Granted"
#     else:
#         print("❌ ACCESS DENIED — Fingerprint Spoof")
#         return "Denied"


# # ---------------------------
# # MAIN
# # ---------------------------
# if __name__ == "__main__":
#     final_result = run_multimodal_verification()
#     print("Final Result:", final_result)     













from load_models import fingerprint_model
from capture_fingerprint import capture_fingerprint
import cv2
import numpy as np


def preprocess_fingerprint(img):

    if img is None:
        return None

    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    return img


def predict_fingerprint():

    img = capture_fingerprint()

    if isinstance(img, str) and img == "FAKE_HARDWARE":
        print("Fingerprint Hardware Spoof Detected")
        return "Spoof", 0.0

    if img is None:
        print("Fingerprint Capture Failed")
        return "Spoof", 0.0

    img_processed = preprocess_fingerprint(img)

    pred = fingerprint_model.predict(img_processed, verbose=0)
    conf = float(pred[0][0])

    THRESHOLD = 0.66

    if conf >= THRESHOLD:
        print(f"Fingerprint LIVE | {conf:.2f}")
        return "Live", conf
    else:
        print(f"Fingerprint SPOOF | {conf:.2f}")
        return "Spoof", conf