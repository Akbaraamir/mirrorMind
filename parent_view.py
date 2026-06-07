# parent_view.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import hashlib

def _generate_anonymous_child_id(child_name):
    """Replicates the safe data minimization hashing token match."""
    if not child_name or str(child_name).strip() == "":
        return "explorer_generic"
    clean_name = str(child_name).strip().lower()
    return hashlib.md5(clean_name.encode('utf-8')).hexdigest()[:10]

def show_weekly_report(child_name, filename="user_history.csv"):
    """
    COPPA-Compliant Parent Analytics Dashboard.
    Filters entries anonymously matching the child's identity hash.
    """
    if not os.path.exists(filename):
        print("⚠️ [ANALYTICS NOTICE]: No ledger data found yet.")
        return

    try:
        df = pd.read_csv(filename)
        if df.empty:
            print("⚠️ [ANALYTICS NOTICE]: The mission ledger is currently empty.")
            return
            
        # Ensure child_id compatibility layer exists
        if "child_id" not in df.columns:
            print("⚠️ [ANALYTICS NOTICE]: Legacy data mismatch detected. Start fresh logs.")
            return

        # Target specific child session blocks safely
        target_id = _generate_anonymous_child_id(child_name)
        df = df[df["child_id"] == target_id].copy()

        if df.empty:
            print(f"⚠️ [ANALYTICS NOTICE]: No session milestones logged yet for '{child_name}'.")
            return

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Reverse map translation layer
        reverse_map = {
            101: "Angry", 102: "Disgust", 103: "Fear", 
            104: "Sad", 105: "Neutral", 106: "Surprise", 107: "Happy"
        }
        df['decoded_emotion'] = df['state_index'].map(reverse_map).fillna("Unknown")

        # Initialize the matplotlib layout engine
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        fig.suptitle(f"🚀 Mission Profile Dashboard: {child_name} Anonymized Index", fontsize=14, weight="bold")

        # CHART 1: UTILITY TRAJECTORY
        ax1.plot(df['timestamp'], df['utility_score'], marker='o', color='#9d4edd', linewidth=2, label='Utility Trend U(S)')
        ax1.axhline(0, color='grey', linestyle='--', linewidth=0.5)
        ax1.set_title("📈 Mood Trajectory (Textbook Utility Index)", fontsize=11, weight="bold")
        ax1.set_ylabel("Utility Value (-1.0 to +1.0)", fontsize=10)
        ax1.grid(True, linestyle=':', alpha=0.6)
        ax1.legend(loc="upper left")
        
        for i, txt in enumerate(df['decoded_emotion']):
            ax1.annotate(f" {txt}", (df['timestamp'].iloc[i], df['utility_score'].iloc[i]), fontsize=9, weight="bold")

        # CHART 2: REFLECTION DEPTH
        ax2.bar(df['timestamp'], df['reflection_depth'], width=0.005, color='#8be9fd', label='Reflection Depth', edgecolor="#6272a4")
        ax2.set_title(" Bars: Engagement & Metacognitive Depth History", fontsize=11, weight="bold")
        ax2.set_xlabel("Mission Timestamp Coordinates", fontsize=10)
        ax2.set_ylabel("Depth Level (0.1 to 1.0)", fontsize=10)
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend(loc="upper left")

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"⚠️ [ANALYTICS ENGINE CRASH]: {e}")