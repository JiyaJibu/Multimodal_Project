import ctypes
import numpy as np

# =========================
# LOAD DLL
# =========================
dll_path = r"C:\Users\jiyaj\OneDrive\Documents\Face Liveness\sgfplib.dll"
sgfplib = ctypes.WinDLL(dll_path)

DWORD = ctypes.c_uint32
HSGFPM = ctypes.c_void_p

# =========================
# FUNCTION PROTOTYPES
# =========================
sgfplib.SGFPM_Create.argtypes = [ctypes.POINTER(HSGFPM)]
sgfplib.SGFPM_Create.restype = DWORD

sgfplib.SGFPM_Init.argtypes = [HSGFPM, DWORD]
sgfplib.SGFPM_Init.restype = DWORD

sgfplib.SGFPM_OpenDevice.argtypes = [HSGFPM, DWORD]
sgfplib.SGFPM_OpenDevice.restype = DWORD

sgfplib.SGFPM_EnableCheckOfFingerLiveness.argtypes = [HSGFPM, ctypes.c_bool]
sgfplib.SGFPM_EnableCheckOfFingerLiveness.restype = DWORD

sgfplib.SGFPM_SetFakeDetectionLevel.argtypes = [HSGFPM, ctypes.c_int]
sgfplib.SGFPM_SetFakeDetectionLevel.restype = DWORD

sgfplib.SGFPM_BeginGetImage.argtypes = [HSGFPM]
sgfplib.SGFPM_BeginGetImage.restype = DWORD

sgfplib.SGFPM_GetImageEx.argtypes = [
    HSGFPM,
    ctypes.POINTER(ctypes.c_ubyte),
    DWORD,
    ctypes.c_void_p,
    DWORD
]
sgfplib.SGFPM_GetImageEx.restype = DWORD

sgfplib.SGFPM_EndGetImage.argtypes = [HSGFPM]
sgfplib.SGFPM_EndGetImage.restype = DWORD

sgfplib.SGFPM_CloseDevice.argtypes = [HSGFPM]
sgfplib.SGFPM_CloseDevice.restype = DWORD

sgfplib.SGFPM_Terminate.argtypes = [HSGFPM]
sgfplib.SGFPM_Terminate.restype = DWORD


# =========================
# CAPTURE FUNCTION
# =========================
def capture_fingerprint():

    hFPM = HSGFPM()

    # 1️⃣ Create object
    if sgfplib.SGFPM_Create(ctypes.byref(hFPM)) != 0:
        print("Create failed")
        return None

    # 2️⃣ Init (AUTO)
    if sgfplib.SGFPM_Init(hFPM, 0xFF) != 0:
        print("Init failed")
        return None

    # 3️⃣ Open first device
    if sgfplib.SGFPM_OpenDevice(hFPM, 0) != 0:
        print("OpenDevice failed")
        return None

    # 4️⃣ Enable hardware fake detection
    sgfplib.SGFPM_EnableCheckOfFingerLiveness(hFPM, True)
    sgfplib.SGFPM_SetFakeDetectionLevel(hFPM, 3)

    width = 300
    height = 400
    buffer_size = width * height
    buffer = (ctypes.c_ubyte * buffer_size)()

    print("👉 Place your finger (10 sec timeout)...")

    sgfplib.SGFPM_BeginGetImage(hFPM)

    timeout = 10000
    quality = 50

    result = sgfplib.SGFPM_GetImageEx(
        hFPM,
        buffer,
        timeout,
        None,
        quality
    )

    sgfplib.SGFPM_EndGetImage(hFPM)

    # 🚨 Hardware fake detection
    if result == 62:
        print("🚨 Hardware detected FAKE finger!")
        sgfplib.SGFPM_CloseDevice(hFPM)
        sgfplib.SGFPM_Terminate(hFPM)
        return "FAKE_HARDWARE"

    if result != 0:
        print("Capture failed:", result)
        sgfplib.SGFPM_CloseDevice(hFPM)
        sgfplib.SGFPM_Terminate(hFPM)
        return None

    print("✅ Fingerprint captured successfully!")

    img = np.frombuffer(buffer, dtype=np.uint8)
    img = img.reshape((height, width))

    sgfplib.SGFPM_CloseDevice(hFPM)
    sgfplib.SGFPM_Terminate(hFPM)

    return img