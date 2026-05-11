from tensorflow.keras.models import load_model

face_model = load_model("models/face_liveness_model.keras", compile=False)
print("Face Model Loaded")



fingerprint_model = load_model("models/fingerprint_liveness_model.keras", compile=False)
print("Fingerprint Model Loaded")

print("Both Models Loaded")