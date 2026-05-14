from collections import Counter

class MirrorMindBrain:
    def __init__(self):
        # Utility weights for different emotions
        self.weights = {
            "angry": -0.8,
            "disgust": -0.6,
            "fear": -0.7,
            "sad": -0.4,
            "neutral": 0.5,
            "surprise": 0.3,
            "happy": 1.0
        }

    def refine_emotion(self, emotion_buffer):
        """Filters noisy data to prevent laughing being read as fear."""
        if not emotion_buffer:
            return "neutral"
            
        counts = Counter(emotion_buffer)
        
        # HEURISTIC: If 'happy' is detected at all in a laughing sequence, 
        # it's likely laughter, not fear.
        if counts['happy'] > 2 and counts['fear'] > 0:
            return "happy"
            
        # Otherwise, return the most frequent emotion (the Mode)
        return counts.most_common(1)[0][0]

    def calculate_utility(self, emotion_list):
        if not emotion_list:
            return 0
        # Calculate average utility of the current buffer
        scores = [self.weights.get(emp, 0) for emp in emotion_list]
        return sum(scores) / len(scores)

    def select_action(self, utility_score, dominant_emotion):
        # Decision Logic: Based on your Phase 2 Roadmap thresholds
        if utility_score < 0:
            return "INTERVENTION_REQUIRED"
        elif utility_score < 0.6:
            return "REFLECTION_PROMPT"
        else:
            return "POSITIVE_REINFORCEMENT"