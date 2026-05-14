import time

def analyze_reflection(user_input, start_time):
    end_time = time.time()
    latency = end_time - start_time
    word_count = len(user_input.split())
    
    # Logic: More words + moderate latency = High Depth
    if word_count > 5 and latency > 3:
        return 1.0 # High engagement
    elif word_count > 0:
        return 0.5 # Moderate
    else:
        return 0.1 # Low/Dismissive