import tkinter as tk
from PIL import Image, ImageTk
import cv2
from face_pipeline import FaceVerifier
from multimodal_pipeline import predict_fingerprint

# Theme Colors
BG_DARK = "#080808"
GRID_COLOR = "#121212"
NEON_GREEN = "#00FF7F"
NEON_RED = "#FF3131"
TEXT_AMBER = "#FFBF00"
GLOW_GREEN = "#004d26"

class SecurityDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("BIOMETRIC ACCESS CONTROL v2.1")
        self.root.geometry("1000x750")
        self.root.configure(bg=BG_DARK)

        self.cap = None
        self.verifier = None
        self.running = False
        self.scan_line_y = 0
        self.countdown_val = 10
        self.final_result_items = []

        self.setup_ui()

    # ---------------- UI SETUP ----------------
    def setup_ui(self):
        self.main_canvas = tk.Canvas(self.root, bg=BG_DARK, highlightthickness=0)
        self.main_canvas.pack(fill="both", expand=True)
        self.draw_grid()

        header = tk.Label(self.root, text="🛡️ BIOMETRIC ACCESS CONTROL 🛡️",
                          font=("OCR A Extended", 24, "bold"),
                          fg="white", bg=BG_DARK)
        self.main_canvas.create_window(500, 60, window=header)

        # Indicators
        self.ind_frame = tk.Frame(self.root, bg=BG_DARK)
        self.face_ind = tk.Label(self.ind_frame, text="[ FACE ]",
                                 font=("Consolas", 12), fg="#444", bg=BG_DARK)
        self.fp_ind = tk.Label(self.ind_frame, text="[ FINGERPRINT ]",
                               font=("Consolas", 12), fg="#444", bg=BG_DARK)
        self.face_ind.pack(side="left", padx=20)
        self.fp_ind.pack(side="left", padx=20)
        self.ind_window = self.main_canvas.create_window(500, 120, window=self.ind_frame)

        # Camera / Scanner Area
        self.view_cont = tk.Frame(self.root, bg="black",
                                  highlightbackground=GLOW_GREEN,
                                  highlightthickness=2)
        self.viewport = tk.Canvas(self.view_cont, width=600, height=400,
                                  bg="black", highlightthickness=0)
        self.viewport.pack()
        self.view_window = self.main_canvas.create_window(500, 350, window=self.view_cont)

        # Instruction Label
        self.instruction_label = tk.Label(self.root, text="SYSTEM STANDBY",
                                          font=("Consolas", 18, "bold"),
                                          fg=TEXT_AMBER, bg=BG_DARK)
        self.inst_window = self.main_canvas.create_window(500, 580,
                                                          window=self.instruction_label)

        # START BUTTON (initial only)
        self.btn_glow = tk.Frame(self.root, bg=NEON_GREEN, padx=2, pady=2)
        self.start_btn = tk.Button(self.btn_glow,
                                   text="START VERIFICATION",
                                   font=("Helvetica", 14, "bold"),
                                   bg="#111", fg=NEON_GREEN,
                                   relief="flat",
                                   width=25, height=2,
                                   command=self.start_verification)
        self.start_btn.pack()
        self.btn_window = self.main_canvas.create_window(500, 480,
                                                         window=self.btn_glow)

    def draw_grid(self):
        for i in range(0, 1000, 40):
            self.main_canvas.create_line(i, 0, i, 750, fill=GRID_COLOR)
        for i in range(0, 750, 40):
            self.main_canvas.create_line(0, i, 1000, i, fill=GRID_COLOR)

    # ---------------- START SYSTEM ----------------
    def start_verification(self):
        self.main_canvas.itemconfigure(self.btn_window, state='hidden')
        self.face_ind.config(fg=NEON_GREEN)
        self.verifier = FaceVerifier()
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.running = True
        self.update_camera()

    # ---------------- CAMERA LOOP ----------------
    def update_camera(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.resize(frame, (600, 400))
        result = self.verifier.update(frame)

        # Display camera
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
        self.viewport.delete("all")
        self.viewport.create_image(0, 0, image=self.photo, anchor="nw")

        # ----- STRICT LOGIC -----
        if result == "ONLY_ONE_PERSON_ALLOWED":
            self.instruction_label.config(text="ONLY ONE PERSON ALLOWED",
                                          fg=NEON_RED)

        elif result == "FACE_SPOOFED":
            self.show_final_result("FACE_SPOOFED")
            return

        elif result == "FACE_CHALLENGE_FAILED":
            self.show_final_result("FACE_CHALLENGE_FAILED")
            return

        elif result == "FACE_VERIFIED":
            self.stop_camera()
            self.start_fingerprint_phase()
            return

        elif result == "RETRY_CHALLENGE":
            self.instruction_label.config(text="CHALLENGE FAILED. RETRYING...",
                                          fg=TEXT_AMBER)

        elif result == "CHALLENGE_ACTIVE":
            instr = self.verifier.challenge.current_instruction
            self.instruction_label.config(text=f"HOLD: {instr.upper()}",
                                          fg=NEON_GREEN)

        else:
            self.instruction_label.config(text=result.replace("_", " "),
                                          fg=TEXT_AMBER)

        self.scan_line_y = (self.scan_line_y + 5) % 400
        self.viewport.create_line(0, self.scan_line_y,
                                  600, self.scan_line_y,
                                  fill=NEON_GREEN, width=2)

        self.root.after(15, self.update_camera)

    # ---------------- FINGERPRINT PHASE ----------------
    def start_fingerprint_phase(self):
        self.face_ind.config(fg="#444")
        self.fp_ind.config(fg=NEON_GREEN)
        self.countdown_val = 5
        self.viewport.delete("all")
        self.viewport.create_oval(220, 80, 380, 320,
                                  outline=NEON_GREEN, width=2)
        self.run_countdown()

    def run_countdown(self):
        if self.countdown_val > 0:
            self.instruction_label.config(
                text=f"PLACE FINGER ({self.countdown_val}s)",
                fg=TEXT_AMBER
            )
            self.countdown_val -= 1
            self.root.after(1000, self.run_countdown)
        else:
            self.process_biometrics()

    def process_biometrics(self):
        self.instruction_label.config(text="ANALYZING FINGERPRINT...",
                                      fg=NEON_GREEN)
        fp_label, fp_conf = predict_fingerprint()

        if fp_label != "Live":
            self.show_final_result("FINGERPRINT_SPOOFED")
        else:
            self.show_final_result("ACCESS_GRANTED")

    # ---------------- FINAL RESULT ----------------
    def show_final_result(self, result_type):
        self.stop_camera()

        self.main_canvas.itemconfigure(self.view_window, state='hidden')
        self.main_canvas.itemconfigure(self.ind_window, state='hidden')
        self.main_canvas.itemconfigure(self.inst_window, state='hidden')

        if result_type == "FACE_SPOOFED":
            main = "FACE SPOOFED"
            sub = "ACCESS DENIED"
            color = NEON_RED

        elif result_type == "FACE_CHALLENGE_FAILED":
            main = "FACE VERIFICATION FAILED"
            sub = "ACCESS DENIED"
            color = NEON_RED

        elif result_type == "FINGERPRINT_SPOOFED":
            main = "FINGERPRINT SPOOFED"
            sub = "ACCESS DENIED"
            color = NEON_RED

        else:
            main = "ACCESS GRANTED"
            sub = "ALL BIOMETRICS VERIFIED"
            color = NEON_GREEN

        result_text = self.main_canvas.create_text(
            500, 330,
            text=f"{main}\n\n{sub}",
            fill=color,
            font=("OCR A Extended", 28, "bold"),
            justify="center"
        )

        # Restart Button
        glow = tk.Frame(self.root, bg=color, padx=2, pady=2)
        btn = tk.Button(glow,
                        text="RESTART SYSTEM",
                        font=("Helvetica", 12, "bold"),
                        bg="#111", fg=color,
                        relief="flat",
                        width=22, height=2,
                        command=self.reset_system)
        btn.pack()

        btn_window = self.main_canvas.create_window(500, 520,
                                                    window=glow)

        self.final_result_items.extend([result_text, btn_window])

    # ---------------- RESET ----------------
    def reset_system(self):
        for item in self.final_result_items:
            self.main_canvas.delete(item)
        self.final_result_items = []

        self.main_canvas.itemconfigure(self.view_window, state='normal')
        self.main_canvas.itemconfigure(self.ind_window, state='normal')
        self.main_canvas.itemconfigure(self.inst_window, state='normal')
        self.main_canvas.itemconfigure(self.btn_window, state='normal')

        self.face_ind.config(fg="#444")
        self.fp_ind.config(fg="#444")
        self.viewport.delete("all")
        self.instruction_label.config(text="SYSTEM STANDBY",
                                      fg=TEXT_AMBER)

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

if __name__ == "__main__":
    root = tk.Tk()
    app = SecurityDashboard(root)
    root.mainloop()