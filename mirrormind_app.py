import cv2
from deepface import DeepFace
import os
import time
from collections import Counter

# Import our modular logic
from brain import MirrorMindBrain
from history_manager import HistoryManager
from reflection_engine import analyze_reflection

# Environment Setup
os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize Components
brain = MirrorMindBrain()
history = HistoryManager()
cap = cv2.VideoCapture(0)

# Persona & Colors
BOT_NAME = "🚀 Pluto"
YELLOW, CYAN, GREEN, RED, END = "\033[93m", "\033[96m", "\033[92m", "\033[91m", "\033[0m"

emotion_buffer = []

print(f"{YELLOW}--- {BOT_NAME} Dashboard Online ---{END}")

while True:
    ret, frame = cap.read()
    if not ret: break

    # --- UI ENHANCEMENT: Boost contrast for better clarity in Karachi lighting ---
    frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=5)

    # 1. PERCEPTION: Capture State
    if int(time.time() * 10) % 2 == 0: 
        try:
            # Using faster, smaller models or enforce_detection=False to keep FPS high
            res = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, detector_backend='opencv')
            emotion_buffer.append(res[0]['dominant_emotion'])
            if len(emotion_buffer) > 15: emotion_buffer.pop(0) 
        except: pass

    # 2. REASONING: Utility & Emotion Refinement
    if emotion_buffer:
        # Use the NEW refine_emotion to filter out the "laughing-fear" glitch
        current_emotion = brain.refine_emotion(emotion_buffer)
        utility_score = brain.calculate_utility(emotion_buffer)
        agent_action = brain.select_action(utility_score, current_emotion)
        
        # --- ACTION: MODERN HUD OVERLAY ---
        # Create semi-transparent overlay bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (640, 100), (30, 10, 10), -1) # Deep space navy
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

        # Dynamic Glow Line (Changes based on Utility)
        # Green for good utility, Cyan for neutral, Red-Pink for low utility
        glow_color = (0, 255, 100) if utility_score > 0.4 else (100, 100, 255)
        cv2.line(frame, (0, 100), (640, 100), glow_color, 2)

        # Dashboard Text
        cv2.putText(frame, f"MISSION STATUS: {current_emotion.upper()}", (20, 40), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
        
        # Map utility to a 0-100% Wellness scale
        wellness_pct = int(((utility_score + 1) / 2) * 100)
        cv2.putText(frame, f"WELLNESS INDEX: {wellness_pct}%", (20, 75), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1)
        
        cv2.putText(frame, "Press [ I ] to Reflect", (420, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow('MirrorMind - Pluto v2.0 Dashboard', frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    # 4. REFLECTION LOOP
    if key == ord('i') and emotion_buffer:
        start_time = time.time()
        print(f"\n{YELLOW}{BOT_NAME}: Space-scan complete!{END}")
        
        from logic_engine import get_pluto_logic 
        ui_content = get_pluto_logic(current_emotion)
        
        print(f"{YELLOW}{BOT_NAME}: {ui_content['msg']}{END}")
        user_input = input(f"{CYAN}You: {END}")
        
        depth = analyze_reflection(user_input, start_time)
        history.log_session(current_emotion, utility_score, depth)
        
        print(f"{GREEN}{BOT_NAME}: Mission Log Updated! {ui_content['task']}{END}")
        print(f"{CYAN}" + "━" * 40 + f"{END}")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()