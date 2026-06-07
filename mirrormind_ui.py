import sys
import os
import time
import random
import threading
import json
import cv2
import customtkinter as ctk
import pyttsx3
from PIL import Image
import queue

# Core backend connections
try:
    from brain import MirrorMindBrain
    from history_manager import HistoryManager
    from reflection_engine import analyze_reflection
    from parental_consent import ParentalConsentGate
    import logic_engine
except ImportError as e:
    class MirrorMindBrain:
        def refine_emotion(self, buf): return buf[-1] if buf else "neutral"
        def calculate_utility(self, buf): return 0.5
    class HistoryManager:
        def log_session(self, child_name, emotion, score, depth=0): pass
    def analyze_reflection(txt, tm): return 0.5

# Multi-User Identity Profile Database
CONFIG_FILE = "user_profiles.json"

class MirrorMindApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("🪐 Captain Pluto's Cosmic Station 🪐")
        self.geometry("1100x670")
        self.resizable(False, False)
        
        # Safe Asynchronous Speech Queue & Worker Thread Setup
        self.speech_queue = queue.Queue()
        threading.Thread(target=self._speech_worker_loop, daemon=True).start()
            
        self.brain = MirrorMindBrain()
        self.history = HistoryManager()
        self.emotion_buffer = []
        self.current_emotion = "neutral"
        self.detected_emotion_snapshot = "neutral"
        self.utility_score = 0.5
        self.reflection_start_time = 0
        self.chat_history = []
        
        self.child_name = "Space Ranger"
        self.child_age = ""
        self.current_language = "en"  
        self.is_processing = False  
        self.interaction_state = "init" 
        self.animation_running = False
        self.temp_password = ""
        
        self.cap = None
        self.is_camera_running = False
        self.latest_tk_frame = None  
        
        # Style Palette
        self.bg_dark = "#0b061a"         
        self.card_bg = "#180f33"         
        self.accent_pink = "#ff59b3"     
        self.accent_blue = "#3ae3ff"     
        self.accent_yellow = "#ffe66d"   
        self.btn_green = "#4ef083"       
        self.text_light = "#ffffff"      
        
        self.main_container = ctk.CTkFrame(self, fg_color=self.bg_dark, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        
        self.star_particles = []
        self.init_starry_decorations()
        self.show_language_screen()
        
        self.ui_camera_refresh_loop()

    def _speech_worker_loop(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 145) 
            voices = engine.getProperty('voices')
            if len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
        except Exception:
            engine = None

        while True:
            text = self.speech_queue.get()
            if text is None or engine is None:
                break
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass
            self.speech_queue.task_done()

    def init_starry_decorations(self):
        for _ in range(35):
            self.star_particles.append({
                "x": random.uniform(0.02, 0.98),
                "y": random.uniform(0.02, 0.98),
                "size": random.choice([2, 3, 4]),
                "color": random.choice([self.accent_pink, self.accent_blue, self.accent_yellow, "#ffffff"])
            })

    def draw_background_stars(self, TargetFrame):
        for star in self.star_particles:
            lbl = ctk.CTkLabel(TargetFrame, text="★", font=ctk.CTkFont(size=star["size"]*4), text_color=star["color"])
            lbl.place(relx=star["x"], rely=star["y"])

    def pluto_speak(self, text_to_say):
        clean_text = ''.join(c for c in text_to_say if ord(c) < 128)
        for stopword in ["🚨", "🌟", "🐾", "😊", "😢", "😡", "😨", "😐", "👉", "✨", "🎮", "🏆", "🪐", "⭐", "👾", "☄️", "🔥", "🛡️", "🛰️", "☁️"]:
            clean_text = clean_text.replace(stopword, "")
        if clean_text.strip():
            self.speech_queue.put(clean_text)

    def clear_ui_layers(self):
        if self.cap:
            self.is_camera_running = False
            self.cap.release()
            self.cap = None
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_language_screen(self):
        self.clear_ui_layers()
        self.draw_background_stars(self.main_container)
        
        title_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        title_frame.pack(pady=(120, 25))
        
        title_lbl = ctk.CTkLabel(title_frame, text="🪐 MIRRORMIND GALAXY 🪐", font=ctk.CTkFont(family="Arial Rounded MT Bold", size=46, weight="bold"), text_color=self.accent_blue)
        title_lbl.pack()
        
        sub_lbl = ctk.CTkLabel(title_frame, text="Choose your language / اپنی زبان منتخب کریں", font=ctk.CTkFont(family="Arial Rounded MT Bold", size=20), text_color=self.accent_yellow)
        sub_lbl.pack(pady=10)
        
        lang_card = ctk.CTkFrame(self.main_container, fg_color=self.card_bg, corner_radius=35, border_width=4, border_color=self.accent_pink, width=480, height=180)
        lang_card.pack_propagate(False)
        lang_card.pack(pady=10)
        
        btn_row = ctk.CTkFrame(lang_card, fg_color="transparent")
        btn_row.pack(expand=True)
        
        en_btn = ctk.CTkButton(btn_row, text="English 🚀", command=lambda: self.select_language("en"), width=160, height=55, corner_radius=22, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=18, weight="bold"), fg_color=self.accent_pink, hover_color="#ff7ec5", text_color="#ffffff")
        en_btn.pack(side="left", padx=15)
        
        ur_btn = ctk.CTkButton(btn_row, text="اردو 🛸", command=lambda: self.select_language("ur"), width=160, height=55, corner_radius=22, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=18, weight="bold"), fg_color=self.accent_blue, hover_color="#7aeaff", text_color=self.bg_dark)
        ur_btn.pack(side="right", padx=15)

    def select_language(self, lang_choice):
        self.current_language = lang_choice
        self.show_landing_screen()

    def show_landing_screen(self):
        self.clear_ui_layers()
        self.draw_background_stars(self.main_container)
        
        title_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        title_frame.pack(pady=(110, 25))
        
        title_lbl = ctk.CTkLabel(title_frame, text="🪐 MIRRORMIND GALAXY 🪐", font=ctk.CTkFont(family="Arial Rounded MT Bold", size=46, weight="bold"), text_color=self.accent_blue)
        title_lbl.pack()
        
        sub_txt = "Look into the space portal and chat with Captain Pluto!" if self.current_language == "en" else "خلائی پورٹل میں دیکھیں اور کیپٹن پلوٹو سے گفتگو کریں!"
        sub_lbl = ctk.CTkLabel(title_frame, text=sub_txt, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=18), text_color=self.accent_yellow)
        sub_lbl.pack(pady=5)
        
        join_card = ctk.CTkFrame(self.main_container, fg_color=self.card_bg, corner_radius=35, border_width=4, border_color=self.accent_pink, width=480, height=200)
        join_card.pack_propagate(False)
        join_card.pack(pady=10)
        
        welcome_str = "Ready to enter the spaceship? ✨" if self.current_language == "en" else "کیا آپ خلائی جہاز میں جانے کے لیے تیار ہیں؟ ✨"
        welcome_txt = ctk.CTkLabel(join_card, text=welcome_str, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=22, weight="bold"), text_color=self.text_light)
        welcome_txt.pack(pady=(40, 20))
        
        login_str = "🔑 Log In" if self.current_language == "en" else "🔑 لاگ ان کریں"
        login_btn = ctk.CTkButton(join_card, text=login_str, command=self.show_login_screen, width=180, height=55, corner_radius=22, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=18, weight="bold"), fg_color=self.accent_blue, hover_color="#7aeaff", text_color=self.bg_dark)
        login_btn.pack(pady=5)

    def show_login_screen(self):
        self.clear_ui_layers()
        self.draw_background_stars(self.main_container)
        
        self.login_box = ctk.CTkFrame(self.main_container, fg_color=self.card_bg, corner_radius=35, border_width=4, border_color=self.accent_pink, width=460, height=450)
        self.login_box.pack_propagate(False)
        self.login_box.pack(pady=80)
        
        if self.current_language == "en":
            title_str = "👋 Welcome Ranger!"
            sub_title_str = "Scan Space Passport (Min 6 Char Password)"
            u_placeholder = "Your space code-name..."
            p_placeholder = "Secret passport password..."
            btn_str = "Verify & Enter Ship! 🛸"
            back_str = "Go Back"
        else:
            title_str = "👋 خوش آمدید خلائی مسافر!"
            sub_title_str = "پاسپورٹ اسکین کریں (پاس ورڈ کم از کم 6 ہندسوں کا ہو)"
            u_placeholder = "آپ کا خفیہ کوڈ نیم..."
            p_placeholder = "خفیہ پاس ورڈ..."
            btn_str = "تصدیق اور جہاز میں داخلہ! 🛸"
            back_str = "پیچھے جائیں"

        self.login_title = ctk.CTkLabel(self.login_box, text=title_str, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=28, weight="bold"), text_color=self.accent_blue)
        self.login_title.pack(pady=(30, 5))
        
        self.login_sub = ctk.CTkLabel(self.login_box, text=sub_title_str, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=13), text_color=self.accent_yellow)
        self.login_sub.pack(pady=(0, 15))
        
        self.u_entry = ctk.CTkEntry(self.login_box, placeholder_text=u_placeholder, width=310, height=48, corner_radius=18, fg_color=self.bg_dark, text_color=self.text_light, border_color=self.accent_blue, font=ctk.CTkFont(size=14))
        self.u_entry.pack(pady=8)
        
        self.p_entry = ctk.CTkEntry(self.login_box, placeholder_text=p_placeholder, show="*", width=310, height=48, corner_radius=18, fg_color=self.bg_dark, text_color=self.text_light, border_color=self.accent_blue, font=ctk.CTkFont(size=14))
        self.p_entry.pack(pady=8)
        
        sub_btn = ctk.CTkButton(self.login_box, text=btn_str, command=self.validate_login_credentials, width=240, height=55, corner_radius=22, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=16, weight="bold"), fg_color=self.btn_green, hover_color="#7cf7a4", text_color=self.bg_dark)
        sub_btn.pack(pady=20)
        
        back_lbl = ctk.CTkLabel(self.login_box, text=back_str, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=14, underline=True), text_color="#9d95b5", cursor="hand2")
        back_lbl.pack()
        back_lbl.bind("<Button-1>", lambda e: self.show_language_screen())

    def validate_login_credentials(self):
        uname = self.u_entry.get().strip()
        pword = self.p_entry.get().strip()
        
        if len(uname) < 2:
            err = "Invalid Identity Profile Name!" if self.current_language == "en" else "غلط کوڈ نیم درج کیا گیا ہے!"
            self.login_sub.configure(text=err, text_color="#ff5555")
            return
            
        if len(pword) < 6:
            err = "Password too short! Must be 6+ characters." if self.current_language == "en" else "پاس ورڈ بہت چھوٹا ہے! کم از کم 6 ہندسے ضروری ہیں۔"
            self.login_sub.configure(text=err, text_color="#ff5555")
            return

        # Core Identity Fix: Fetch the full profiles catalog table
        profiles = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    profiles = json.load(f)
            except Exception:
                profiles = {}

        # Set identity globally
        self.child_name = uname

        if uname in profiles:
            # RETURNING USER MATCH: Verify Secret Password Matrix
            if profiles[uname]["password"] == pword:
                self.child_age = profiles[uname]["age"]
                print(f"🔑 [PROFILE SYNC]: Welcome back Ranger {self.child_name} (Age: {self.child_age})")
                ParentalConsentGate(parent_app=self, on_success_callback=self.initialize_main_galaxy)
            else:
                err = "Incorrect passport password entry!" if self.current_language == "en" else "غلط پاس ورڈ درج کیا گیا ہے!"
                self.login_sub.configure(text=err, text_color="#ff5555")
        else:
            # NEW USER DETECTED: Stage credentials temporarily, pass through Parental gate to onboarding
            self.temp_password = pword
            print(f"✨ [NEW EXPLORER]: Profiling new token path for {self.child_name}")
            ParentalConsentGate(parent_app=self, on_success_callback=self.show_onboarding_dialog)

    def show_onboarding_dialog(self):
        self.clear_ui_layers()
        self.draw_background_stars(self.main_container)
        
        self.onboard_card = ctk.CTkFrame(self.main_container, fg_color=self.card_bg, corner_radius=35, border_width=4, border_color=self.accent_yellow, width=470, height=390)
        self.onboard_card.pack_propagate(False)
        self.onboard_card.pack(pady=110)
        
        greet_str = f"🐾 'Beep Boop!' 🐾\nWelcome to the crew, Ranger {self.child_name}!\nHow old are you?" if self.current_language == "en" else f"🐾 'بیپ بوپ!' 🐾\nخوش آمدید خلائی مسافر {self.child_name}!\nآپ کی عمر کتنی ہے؟"
        age_placeholder = "How old are you? (Max 12)" if self.current_language == "en" else "آپ کی عمر کتنی ہے? (زیادہ سے زیادہ 12)"
        btn_str = "Blast Off! 🎉" if self.current_language == "en" else "فلائٹ شروع کریں! 🎉"

        self.greet_lbl = ctk.CTkLabel(self.onboard_card, text=greet_str, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=20, weight="bold"), text_color=self.text_light, justify="center")
        self.greet_lbl.pack(pady=(45, 25))
        
        self.age_field = ctk.CTkEntry(self.onboard_card, placeholder_text=age_placeholder, width=310, height=48, corner_radius=18, fg_color=self.bg_dark, text_color=self.text_light, border_color=self.accent_blue, justify="center", font=ctk.CTkFont(size=14))
        self.age_field.pack(pady=8)
        self.age_field.focus()
        
        self.go_btn = ctk.CTkButton(self.onboard_card, text=btn_str, command=self.save_onboarding_details, width=210, height=55, corner_radius=22, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=17, weight="bold"), fg_color=self.accent_pink, hover_color="#ff7ec5", text_color="#ffffff")
        self.go_btn.pack(pady=25)

    def save_onboarding_details(self):
        provided_age = self.age_field.get().strip()
        
        try:
            age_int = int(provided_age)
            if age_int > 12:
                err_msg = "🚨 ACCESS DENIED! 🚨\nThis Cosmic Station is for Junior Rangers aged 12 or below!" if self.current_language == "en" else "🚨 داخلہ ممنوع ہے! 🚨\nیہ خلائی اسٹیشن صرف 12 سال یا اس سے کم عمر کے بچوں کے لیے ہے!"
                self.greet_lbl.configure(text=err_msg, text_color="#ff5555", font=ctk.CTkFont(family="Arial Rounded MT Bold", size=15, weight="bold"))
                self.age_field.delete(0, "end")
                return
            if age_int <= 0:
                raise ValueError()
        except ValueError:
            err_invalid = "Please enter a valid age number!" if self.current_language == "en" else "براہ کرم درست عمر درج کریں!"
            self.greet_lbl.configure(text=err_invalid, text_color="#ff5555")
            return

        self.child_age = str(age_int)

        # Append new profile record without wiping old database indexes
        profiles = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    profiles = json.load(f)
            except Exception:
                profiles = {}

        profiles[self.child_name] = {
            "password": getattr(self, "temp_password", "123456"),
            "age": self.child_age
        }

        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(profiles, f, indent=4)
            print(f"💾 [DATABASE WRITTEN]: Profile committed safely for {self.child_name}")
        except Exception as error:
            print(f"⚠️ [DATABASE STORAGE TRAPPED]: {error}")

        self.initialize_main_galaxy()

    def initialize_main_galaxy(self):
        self.clear_ui_layers()
        self.draw_background_stars(self.main_container)
        self.is_processing = False
        
        left_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=(25, 12), pady=25)
        
        radar_str = "📡 Syncing Cosmic Radar Feed..." if self.current_language == "en" else "📡 کاسمک ریڈار فیڈ لنک ہو رہی ہے..."
        self.live_indicator = ctk.CTkLabel(left_panel, text=radar_str, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=16, weight="bold"), fg_color=self.accent_yellow, text_color=self.bg_dark, height=45, corner_radius=18)
        self.live_indicator.pack(fill="x", pady=(0, 12))
        
        cam_card = ctk.CTkFrame(left_panel, fg_color=self.card_bg, border_width=4, border_color=self.accent_pink, corner_radius=30)
        cam_card.pack(fill="both", expand=True)
        
        optics_str = "Aligning Space Optics Mirror..." if self.current_language == "en" else "اسپیس آپٹکس آئینے کی ترتیب..."
        self.cam_label = ctk.CTkLabel(cam_card, text=optics_str, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=14), text_color="#897fa1")
        self.cam_label.pack(fill="both", expand=True, padx=12, pady=12)
        
        right_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=(12, 25), pady=25)
        
        self.terminal = ctk.CTkFrame(right_panel, fg_color=self.card_bg, border_width=4, border_color=self.accent_blue, corner_radius=30)
        self.terminal.pack(fill="both", expand=True)
        
        header_text = f"🚀 Ranger {self.child_name}! 🚀" if self.current_language == "en" else f"🚀 خلائی مسافر {self.child_name}! 🚀"
        welcome_header = ctk.CTkLabel(self.terminal, text=header_text, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=26, weight="bold"), text_color=self.accent_pink)
        welcome_header.pack(pady=(25, 5))
        
        self.bubble = ctk.CTkTextbox(self.terminal, font=ctk.CTkFont(family="Courier New", size=14), fg_color=self.bg_dark, text_color=self.text_light, corner_radius=22, wrap="word")
        self.bubble.pack(fill="both", expand=True, padx=20, pady=12)
        
        if self.current_language == "en":
            welcome_greet = f"Hi {self.child_name}! Let's scan your facial sensors to calibrate our transmission link. Click the button below!"
            placeholder_terminal = "Whisper back to Pluto over the terminal..."
        else:
            welcome_greet = f"سلام {self.child_name}! لنک سیٹ کرنے کے لیے نیچے والا بٹن دبائیں۔"
            placeholder_terminal = "ٹرمینل کے ذریعے پلوٹو کو جواب دیں..."

        self.set_bubble_content(welcome_greet)
        
        self.kid_input = ctk.CTkEntry(self.terminal, placeholder_text=placeholder_terminal, height=48, corner_radius=18, fg_color=self.bg_dark, text_color=self.text_light, border_color=self.accent_yellow, font=ctk.CTkFont(size=14))
        self.kid_input.pack(fill="x", padx=20, pady=8)
        
        self.action_btn = ctk.CTkButton(self.terminal, text="", height=55, corner_radius=22, font=ctk.CTkFont(family="Arial Rounded MT Bold", size=16, weight="bold"))
        self.action_btn.pack(fill="x", padx=20, pady=(5, 25))
        
        self.setup_scanning_phase()
        
        self.cap = cv2.VideoCapture(0)
        self.is_camera_running = True
        threading.Thread(target=self.camera_stream_tick, daemon=True).start()
        self.pluto_speak(welcome_greet)

    def camera_stream_tick(self):
        while self.is_camera_running and self.cap is not None:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.03)
                continue
                
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            if random.random() < 0.04:
                try:
                    from deepface import DeepFace
                    res = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    detected = res[0]['dominant_emotion']
                    self.emotion_buffer.append(detected)
                    if len(self.emotion_buffer) > 5:
                        self.emotion_buffer.pop(0)
                    self.detected_emotion_snapshot = self.brain.refine_emotion(self.emotion_buffer)
                except Exception:
                    pass

            img = Image.fromarray(frame_rgb)
            self.latest_tk_frame = ctk.CTkImage(light_image=img, dark_image=img, size=(440, 390))
            time.sleep(0.03)

    def ui_camera_refresh_loop(self):
        if self.is_camera_running and self.latest_tk_frame:
            try:
                self.cam_label.configure(image=self.latest_tk_frame, text="")
                self.cam_label.img_tk = self.latest_tk_frame
            except Exception:
                pass

        if self.is_camera_running:
            emoji_map = {"happy": "😊 Happy", "sad": "😢 Sad", "angry": "😡 Angry", "fear": "😨 Scared", "neutral": "😐 Neutral"}
            translated = emoji_map.get(self.detected_emotion_snapshot, "😐 Neutral")
            prefix = "Live Metrics: " if self.current_language == "en" else "لائیو تاثرات: "
            try:
                self.live_indicator.configure(text=f"{prefix}{translated}")
            except Exception:
                pass
                
        self.after(30, self.ui_camera_refresh_loop)

    def set_bubble_content(self, txt_content):
        self.bubble.configure(state="normal")
        self.bubble.delete("0.0", "end")
        self.bubble.insert("0.0", txt_content)
        self.bubble.configure(state="disabled")

    def animate_loading_dots(self, frame_count=0):
        if not self.animation_running:
            return
        
        star_x = random.randint(100, 999)
        star_y = random.randint(100, 999)
        beam_frequency = round(random.uniform(12.4, 98.9), 2)
        shield_percentage = random.randint(85, 100)
        
        vis_matrix = (
            f"🛰️ COMPILING TRANSMISSION SIGNAL OVER NEURAL NETWORK...\n"
            f"----------------------------------------------------\n"
            f"📡 Radar Locks   : [X:{star_x} | Y:{star_y}]\n"
            f"☄️ Comet Streams : {beam_frequency} MHz\n"
            f"🛡️ Shield Matrix : {shield_percentage}% Safe!\n"
            f"----------------------------------------------------\n\n"
            f"    Pluto's space ears are listening to you... 🐾\n\n"
        )
        
        progress_blocks = "■" * (frame_count % 12 + 1)
        dots_trail = "• " * (12 - (frame_count % 12 + 1))
        vis_matrix += f"    📡 CONNECTING: [{progress_blocks}{dots_trail}]"
        
        self.set_bubble_content(vis_matrix)
        self.after(120, lambda: self.animate_loading_dots(frame_count + 1))

    def clear_all_inputs(self):
        try:
            self.kid_input.unbind("<Return>")
        except Exception:
            pass
        self.action_btn.configure(command=None)

    def setup_scanning_phase(self):
        self.clear_all_inputs()
        self.interaction_state = "scanning"
        btn_action_str = "✨ TRANSMIT FACE SCAN SNAPSHOT! ✨" if self.current_language == "en" else "✨ چہرے کا اسکین اسنیپ شاٹ لیں! ✨"
        self.action_btn.configure(text=btn_action_str, fg_color=self.btn_green, text_color=self.bg_dark, command=self.exec_scanning_action)
        self.kid_input.bind("<Return>", lambda e: self.exec_scanning_action())

    def exec_scanning_action(self, event=None):
        if self.interaction_state != "scanning":
            return
        self.clear_all_inputs()
        self.interaction_state = "confirming"
        
        self.current_emotion = self.detected_emotion_snapshot
        self.utility_score = self.brain.calculate_utility([self.current_emotion])
        meta_rules = logic_engine.get_pluto_logic(self.current_emotion)
        
        if self.current_language == "en":
            display_text = f"Pluto locked your expression matrix as:\n👉 {meta_rules['emoji']} {self.current_emotion.upper()}\n\n{meta_rules['msg']}\n\n✨ Mission Task: {meta_rules['task']}"
            btn_confirm = "Begin Log Entry 👍"
        else:
            display_text = f"پلوٹو نے ریڈار لاک مکمل کر لیا ہے:\n👉 {meta_rules['emoji']}\n\n{meta_rules['msg']}\n\n✨ کام: {meta_rules['task']}"
            btn_confirm = "تصدیق کریں 👍"

        self.set_bubble_content(display_text)
        self.pluto_speak(meta_rules['msg'])
        
        self.action_btn.configure(text=btn_confirm, fg_color=self.accent_yellow, text_color=self.bg_dark, command=self.exec_confirming_action)
        self.kid_input.bind("<Return>", lambda e: self.exec_confirming_action())
        self.kid_input.focus()

    def exec_confirming_action(self, event=None):
        if self.interaction_state != "confirming":
            return
        self.clear_all_inputs()
        self.interaction_state = "journaling"
        self.kid_input.delete(0, "end")
        self.reflection_start_time = time.time()
        
        if self.current_language == "en":
            display_text = f"Transmission channel completely open!\n\nCaptain {self.child_name}, type into the space log terminal: What is on your mind today?"
            tts_text = "Transmission received! Please tell me what is on your mind."
            btn_txt = "Transmit Answer 💬"
        else:
            display_text = f"سگنل موصول ہو گیا!\n\nپیارے خلائی مسافر {self.child_name}، ٹرمینل پر لکھیں: آج آپ کے دل میں کیا بات ہے؟"
            tts_text = "Please write down what happened today."
            btn_txt = "جواب بھیجیں 💬"

        self.set_bubble_content(display_text)
        self.pluto_speak(tts_text)
        
        self.action_btn.configure(text=btn_txt, fg_color=self.accent_blue, text_color=self.bg_dark, command=self.exec_journaling_action)
        self.kid_input.bind("<Return>", lambda e: self.exec_journaling_action())

    def exec_journaling_action(self, event=None):
        if self.interaction_state != "journaling" or self.is_processing:
            return
            
        journal_text = self.kid_input.get().strip()
        if len(journal_text) < 2:
            return
            
        self.is_processing = True
        self.clear_all_inputs()
        
        self.kid_input.delete(0, "end")
        self.action_btn.configure(state="disabled")
        self.kid_input.configure(state="disabled")
        
        child_reply_lower = journal_text.lower()
        if "bye" in child_reply_lower or "exit" in child_reply_lower or "خدا حافظ" in child_reply_lower:
            self.interaction_state = "goodbye"
            if self.current_language == "ur":
                goodbye_display = f"خدا حافظ پیارے خلائی مسافر {self.child_name}! 👋"
                btn_exit = "اسٹیشن بند کریں 🚪"
            else:
                goodbye_display = f"Goodbye, Ranger {self.child_name}! Khuda Hafiz! 👋"
                btn_exit = "Shut Down Station 🚪"
                
            self.set_bubble_content(goodbye_display)
            self.pluto_speak(goodbye_display)
            self.action_btn.configure(state="normal", text=btn_exit, fg_color="#ff5555", text_color="#ffffff", command=self.on_closing)
            return

        self.animation_running = True
        self.animate_loading_dots()
        
        loading_btn = "Processing... ⏳" if self.current_language == "en" else "انتظار کریں... ⏳"
        self.action_btn.configure(text=loading_btn, fg_color="#555555", text_color="#aaaaaa")

        frozen_emotion = self.current_emotion
        frozen_utility = self.utility_score
        frozen_start_time = self.reflection_start_time
        
        history_context = ""
        if self.chat_history:
            history_context = "\n".join([f"{m['role']}: {m['content']}" for m in self.chat_history[-4:]])

        def process_llm_generation(txt, start_tm, context_str, emo, util):
            calculated_depth = analyze_reflection(txt, start_tm)
            
            cleaned_input = txt.lower().strip()
            if any(sad_word in cleaned_input for sad_word in ["sad", "udaas", "rhena", "crying", "hurt", "bad day"]):
                ai_response = f"I hear you loud and clear, my dear beta. Please do not be pareshan. Even the brightest stars in the galaxy sometimes hide behind dark clouds. Let's take a deep breath together to find some sukoon. You are doing great, and Captain Pluto is right here with you!"
                self.after(0, lambda: self.finalize_llm_response(txt, ai_response, emo, util, calculated_depth))
                return

            try:
                import ollama
                
                system_instructions = (
                    f"You are Captain Pluto, a warm, soft-spoken child-friendly space therapist dog. "
                    f"You are speaking with {self.child_name}, age {self.child_age}.\n\n"
                    f"STRICT SYSTEM ARCHITECTURE DIRECTIVES:\n"
                    f"1. Baseline Language: Respond strictly in pure, natural, comforting English sentences.\n"
                    f"2. Forbidden Syntax: Do NOT output broken mixed grammar structures, structural Roman Urdu fragments, or generic refusal templates like 'I cannot fulfill your request'.\n"
                    f"3. CRITICAL WORD USAGE MUTUAL EXCLUSIVITY:\n"
                    f"   - Never, under any circumstances, use the words 'bhai' and 'beta' in the same response. They are completely contradictory.\n"
                    f"   - Choose ONLY ONE focus term per response if you wish to express closeness:\n"
                    f"     * Use 'beta' if you want to sound like a gentle, protective cosmic guide.\n"
                    f"     * Use 'bhai' if you want to sound like a supportive space crew friend.\n"
                    f"   - Ensure the chosen term blends naturally into proper English syntax (e.g., 'Don't worry, beta, we can solve this together' or 'I am right here with you, bhai.').\n"
                    f"4. Prohibited Pairings: Do not string affection keywords back-to-back (e.g., do not write 'bhai beta' or 'sukoon pareshan').\n\n"
                    f"COUNSELING SCHEDULER:\n"
                    f"- Max sentence length: 2 to 3 sentences total.\n"
                    f"- Validate their primary emotion, express validation, and deliver exactly ONE simple real-world action item."
                )
                
                full_prompt_payload = (
                    f"System Directives:\n{system_instructions}\n\n"
                    f"Previous Conversation Thread:\n{context_str}\n\n"
                    f"Child Ranger typed: '{txt}'\n"
                    f"Captain Pluto's Direct Action Response:"
                )
                
                response = ollama.generate(
                    model='llama3.2:1b',
                    prompt=full_prompt_payload
                )
                ai_response = response['response']
                
                # Structural Safety Sweep: Strict cleanup in case the engine slips up
                if "bhai" in ai_response.lower() and "beta" in ai_response.lower():
                    ai_response = ai_response.replace("bhai", "").replace("Bhai", "")
                
                if "fulfill" in ai_response.lower() or "cannot" in ai_response.lower() or "apologize" in ai_response.lower():
                    raise ValueError("Model fallback triggered due to structural refusal text.")
                
            except Exception as error_diagnostics:
                print(f"\n🚨 OLLAMA FILTER/CRASH BYPASS LOG: {error_diagnostics}\n")
                ai_response = f"I hear you loud and clear, my dear beta. Please do not be pareshan. Let's take a deep breath together to find some sukoon. You are doing great!"

            self.after(0, lambda: self.finalize_llm_response(txt, ai_response, emo, util, calculated_depth))
            
        threading.Thread(target=process_llm_generation, args=(journal_text, frozen_start_time, history_context, frozen_emotion, frozen_utility), daemon=True).start()

    def finalize_llm_response(self, original_text, ai_response, emo, util, depth):
        self.animation_running = False  
        
        self.chat_history.append({"role": "user", "content": original_text})
        self.chat_history.append({"role": "assistant", "content": ai_response})
        
        self.history.log_session(
            child_name=self.child_name, 
            emotion=emo, 
            score=util, 
            depth=depth
        )
        
        suffix = "\n\nType back to Pluto to keep chatting, or type 'bye' to exit." if self.current_language == "en" else "\n\nبات جاری رکھنے کے لیے یہاں ٹائپ کریں، یا بند کرنے کے لیے 'bye' لکھیں۔"
        self.set_bubble_content(f"{ai_response}{suffix}")
        
        self.kid_input.configure(state="normal")
        self.action_btn.configure(state="normal")
        
        try:
            self.kid_input.unbind("<Return>")
        except Exception:
            pass
            
        btn_next = "Transmit Reply ⚡" if self.current_language == "en" else "پیغام بھیجیں ⚡"
        self.action_btn.configure(text=btn_next, fg_color=self.accent_pink, text_color="#ffffff", command=self.exec_journaling_action)
        self.kid_input.bind("<Return>", lambda e: self.exec_journaling_action())
        
        self.is_processing = False
        self.interaction_state = "journaling"
        self.reflection_start_time = time.time()
        
        self.after(50, lambda: self.kid_input.delete(0, "end"))
        self.after(100, lambda: self.kid_input.focus_set())
        
        self.pluto_speak(ai_response)

    def on_closing(self):
        self.is_camera_running = False
        self.speech_queue.put(None)  
        if self.cap:
            self.cap.release()
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = MirrorMindApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    