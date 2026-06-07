# parental_consent.py
import random
import customtkinter as ctk

class ParentalConsentGate(ctk.CTkToplevel):
    def __init__(self, parent_app, on_success_callback):
        """
        COPPA Compliance Entry Gate Component.
        Blocks application execution until an adult solves a simplified
        single-digit addition puzzle.
        """
        super().__init__()
        self.parent_app = parent_app
        self.on_success_callback = on_success_callback
        
        # Configure Window Properties
        self.title("🛡️ COPPA Security Verification Gate")
        self.geometry("500x380")
        self.resizable(False, False)
        self.configure(fg_color="#120c1f")
        
        # Ensure focus stays on this window (Modal Dialog Paradigm)
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()
        
        # Intercept closing the window manually to prevent bypassing the gate
        self.protocol("WM_DELETE_WINDOW", self.on_force_quit)
        
        # EASY SINGLE-DIGIT CHALLENGE PARAMETERS
        self.num1 = random.randint(3, 9)
        self.num2 = random.randint(3, 9)
        self.correct_answer = self.num1 + self.num2
        
        self.init_ui_elements()

    def init_ui_elements(self):
        header_lbl = ctk.CTkLabel(
            self, 
            text="🔒 GROWN-UPS ONLY", 
            font=ctk.CTkFont(family="Arial Rounded MT Bold", size=24, weight="bold"),
            text_color="#3ae3ff"
        )
        header_lbl.pack(pady=(35, 10))
        
        coppa_notice = (
            "To comply with privacy laws and open the webcam link,\n"
            "a parent or guardian must verify this entry step."
        )
        notice_lbl = ctk.CTkLabel(
            self, 
            text=coppa_notice, 
            font=ctk.CTkFont(size=13),
            text_color="#ffffff",
            justify="center"
        )
        notice_lbl.pack(pady=5)
        
        self.challenge_lbl = ctk.CTkLabel(
            self, 
            text=f"Prove you are a Grown-Up Space Ranger:\nWhat is {self.num1} + {self.num2}?", 
            font=ctk.CTkFont(family="Arial Rounded MT Bold", size=16, weight="bold"),
            text_color="#ffe66d",
            justify="center"
        )
        self.challenge_lbl.pack(pady=20)
        
        self.answer_input = ctk.CTkEntry(
            self, 
            placeholder_text="Type answer here...",
            width=200, 
            height=40, 
            corner_radius=12,
            fg_color="#1a1136", 
            text_color="#ffffff", 
            border_color="#ff59b3",
            justify="center",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.answer_input.pack(pady=5)
        self.answer_input.bind("<Return>", lambda e: self.verify_challenge())
        
        self.error_lbl = ctk.CTkLabel(
            self, 
            text="", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ff5555"
        )
        self.error_lbl.pack(pady=5)
        
        verify_btn = ctk.CTkButton(
            self, 
            text="Verify Consent & Launch ✔", 
            command=self.verify_challenge,
            width=220, 
            height=45, 
            corner_radius=15,
            fg_color="#4ef083", 
            hover_color="#7cf7a4", 
            text_color="#120c1f",
            font=ctk.CTkFont(family="Arial Rounded MT Bold", size=14, weight="bold")
        )
        verify_btn.pack(pady=(10, 15))

    def verify_challenge(self):
        user_response = self.answer_input.get().strip()
        try:
            if int(user_response) == self.correct_answer:
                print("🔒 [COPPA VERIFIED]: Verifiable Parental Consent granted successfully.")
                self.grab_release()
                self.destroy() 
                self.on_success_callback() 
            else:
                raise ValueError
        except (ValueError, TypeError):
            self.error_lbl.configure(text="❌ Recalculating coordinates... Incorrect entry. Try again.")
            self.answer_input.delete(0, "end")
            
            self.num1 = random.randint(3, 9)
            self.num2 = random.randint(3, 9)
            self.correct_answer = self.num1 + self.num2
            self.challenge_lbl.configure(text=f"Prove you are a Grown-Up Space Ranger:\nWhat is {self.num1} + {self.num2}?")

    def on_force_quit(self):
        print("🚨 [SECURITY ENFORCEMENT]: Consent gate closed without confirmation.")
        self.grab_release()
        self.destroy()
        if self.parent_app and hasattr(self.parent_app, 'on_closing'):
            self.parent_app.on_closing()