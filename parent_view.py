import pandas as pd
import matplotlib.pyplot as plt

def show_weekly_report():
    try:
        df = pd.read_csv("user_history.csv")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        plt.figure(figsize=(10, 5))
        plt.plot(df['timestamp'], df['utility_score'], marker='o', color='cyan')
        plt.title("Child's Emotional Well-being Trend (Pluto Data)")
        plt.xlabel("Time")
        plt.ylabel("Utility (Wellness) Score")
        plt.grid(True)
        plt.show()
    except Exception as e:
        print("No data found yet. Start your mission with Pluto first!")

# show_weekly_report()