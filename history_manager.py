import pandas as pd
from datetime import datetime
import os

class HistoryManager:
    def __init__(self, filename="user_history.csv"):
        self.filename = filename
        if not os.path.exists(self.filename):
            df = pd.DataFrame(columns=["timestamp", "emotion", "utility_score", "reflection_depth"])
            df.to_csv(self.filename, index=False)

    def log_session(self, emotion, score, depth=0):
        new_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "emotion": emotion,
            "utility_score": round(score, 2),
            "reflection_depth": depth
        }
        df = pd.read_csv(self.filename)
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv(self.filename, index=False)
        print(f"✅ Session Logged: {emotion} (U: {score})")