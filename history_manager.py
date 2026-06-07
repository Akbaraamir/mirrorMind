# history_manager.py
import pandas as pd
from datetime import datetime
import os
import hashlib

class HistoryManager:
    def __init__(self, filename="user_history.csv"):
        self.filename = filename
        if not os.path.exists(self.filename):
            # IMPLEMENTATION PLACE 1: Setup baseline file structure
            df = pd.DataFrame(columns=["timestamp", "child_id", "state_index", "utility_score", "reflection_depth"])
            df.to_csv(self.filename, index=False)

    def _generate_anonymous_child_id(self, child_name):
        """Generates a secure, data-minimized profile token."""
        if not child_name or str(child_name).strip() == "":
            return "explorer_generic"
        clean_name = str(child_name).strip().lower()
        return hashlib.md5(clean_name.encode('utf-8')).hexdigest()[:10]

    def log_session(self, child_name, emotion, score, depth=0):
        """Logs interactive session states into numerical index representations."""
        biometric_obfuscation_map = {
            "angry": 101, "disgust": 102, "fear": 103,
            "sad": 104, "neutral": 105, "surprise": 106, "happy": 107
        }
        anonymous_state_index = biometric_obfuscation_map.get(emotion, 105)
        child_id = self._generate_anonymous_child_id(child_name)

        # Build data row matching the new columns
        new_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "child_id": child_id,
            "state_index": anonymous_state_index, 
            "utility_score": round(score, 2),
            "reflection_depth": depth
        }
        
        try:
            df = pd.read_csv(self.filename)
            # Migration path: add column if reading an older file version
            if "child_id" not in df.columns:
                df["child_id"] = "explorer_generic"
            
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(self.filename, index=False)
            print(f"✅ Session Logged: {child_id} (State: {anonymous_state_index})")
        except Exception as e:
            print(f"⚠️ [DATABASE ERROR]: {e}")
        
    def get_last_session_context(self, child_name):
        """Retrieves the last known mood context for this specific child profile token."""
        reverse_map = {
            101: "angry", 102: "disgust", 103: "fear", 
            104: "sad", 105: "neutral", 106: "surprise", 107: "happy"
        }
        child_id = self._generate_anonymous_child_id(child_name)
        
        try:
            if os.path.exists(self.filename):
                df = pd.read_csv(self.filename)
                if not df.empty and "child_id" in df.columns:
                    child_history = df[df["child_id"] == child_id]
                    if not child_history.empty:
                        last_row = child_history.iloc[-1]
                        return reverse_map.get(int(last_row["state_index"]), "neutral")
        except Exception as e:
            print(f"⚠️ [CONTEXT FETCH ERROR]: {e}")
        return "neutral"