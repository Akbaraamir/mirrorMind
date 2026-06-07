# brain.py
from collections import Counter
import json
import ollama

class MirrorMindBrain:
    def __init__(self, model_name="llama3.2:1b"):
        self.model_name = model_name
        
        # CHAPTER 15.1: Textbook Utility Weights U(S) for State Space
        self.weights = {
            "angry": -0.8,
            "disgust": -0.6,
            "fear": -0.7,
            "sad": -0.4,
            "neutral": 0.5,
            "surprise": 0.3,
            "happy": 1.0
        }

        # CHAPTER 16.1: Transition Probability Model Matrix P(S' | S, A)
        # Formatted as: [Current State][Action Option] -> Probability distribution of next state S'
        # Actions: 'mindfulness' (grounding), 'physical_break' (screen breakaway), 'expressive' (journaling)
        self.transition_model = {
            "sad": {
                "mindfulness":   {"sad": 0.30, "neutral": 0.50, "happy": 0.20},
                "physical_break": {"sad": 0.20, "neutral": 0.60, "happy": 0.20},
                "expressive":     {"sad": 0.40, "neutral": 0.40, "happy": 0.20}
            },
            "angry": {
                "mindfulness":   {"angry": 0.20, "neutral": 0.60, "happy": 0.20},
                "physical_break": {"angry": 0.40, "neutral": 0.50, "happy": 0.10},
                "expressive":     {"angry": 0.50, "neutral": 0.40, "happy": 0.10}
            },
            "fear": {
                "mindfulness":   {"fear": 0.15, "neutral": 0.65, "happy": 0.20},
                "physical_break": {"fear": 0.50, "neutral": 0.40, "happy": 0.10},
                "expressive":     {"fear": 0.40, "neutral": 0.50, "happy": 0.10}
            },
            "neutral": {
                "mindfulness":   {"neutral": 0.70, "happy": 0.30},
                "physical_break": {"neutral": 0.60, "happy": 0.40},
                "expressive":     {"neutral": 0.50, "happy": 0.50}
            },
            "happy": {
                "mindfulness":   {"neutral": 0.20, "happy": 0.80},
                "physical_break": {"neutral": 0.30, "happy": 0.70},
                "expressive":     {"neutral": 0.10, "happy": 0.90}
            }
        }

        # Counseling Advice Vault mapped to the quantitative actions
        self.action_vault = {
            "mindfulness": "Take 3 deep breaths and look for three blue things around your star cabin to ground your sensory matrix.",
            "physical_break": "Park your space screen for 5 minutes and march around your command deck to shake out old cosmic fuel.",
            "expressive": "Type or write out one bright thing that happened on your Earth mission today to log in your captain's vault."
        }

    def refine_emotion(self, emotion_buffer):
        """Filters noisy camera streams to capture real dominant states."""
        if not emotion_buffer:
            return "neutral"
        counts = Counter(emotion_buffer)
        if counts['happy'] > 2 and counts['fear'] > 0:
            return "happy"
        return counts.most_common(1)[0][0]

    def calculate_utility(self, emotion_list):
        """Calculates current emotional state utility baseline."""
        if not emotion_list:
            return 0.0
        scores = [self.weights.get(emp, 0.0) for emp in emotion_list]
        return sum(scores) / len(scores)

    def select_optimal_action(self, current_emotion, dynamic_override_action=None):
        """
        CHAPTER 16.2: MAXIMUM EXPECTED UTILITY (MEU) DECISION ENGINE
        Calculates EU(A | E) = Sum( P(S' | S, A) * U(S') ) for all available actions
        and returns the action key and advice text.
        """
        if current_emotion not in self.transition_model:
            current_emotion = "neutral"

        if dynamic_override_action and dynamic_override_action in self.action_vault:
            print(f"🔄 [AGENTIC WORKFLOW PIVOT]: Overriding math defaults to avoid repetitive loop. Selecting: {dynamic_override_action}")
            return dynamic_override_action, self.action_vault[dynamic_override_action]

        best_action = None
        max_expected_utility = -999.0

        for action, state_transitions in self.transition_model[current_emotion].items():
            expected_utility = 0.0
            for next_state, probability in state_transitions.items():
                target_utility = self.weights.get(next_state, 0.0)
                expected_utility += probability * target_utility
            
            print(f"📊 Evaluated Strategy [{action}] -> Expected Utility: {round(expected_utility, 3)}")
            
            if expected_utility > max_expected_utility:
                max_expected_utility = expected_utility
                best_action = action

        print(f"🏆 MEU Choice: [{best_action}] maximizing expected utility at {round(max_expected_utility, 3)}")
        return best_action, self.action_vault[best_action]

    def agentic_reflection(self, last_emotion, current_emotion):
        """
        CRITIQUE STEP: Evaluates if previous guidance successfully converted user utility.
        """
        negative_states = ["sad", "angry", "fear"]
        if last_emotion in negative_states and current_emotion in negative_states:
            if current_emotion == "angry":
                return "physical_break"
            if current_emotion == "sad":
                return "mindfulness"
        return None

    def generate_interactive_bilingual_response(self, child_input, active_emotion, child_name):
        """
        Calls the local Ollama instance with specialized child-therapy prompt constraints.
        Returns a structured dictionary matching the expected UI format.
        """
        # Calculate optimal strategy guidance based on current emotion metrics
        best_action_key, action_advice = self.select_optimal_action(active_emotion)
        
        # System instructions designed to promote warmth, therapeutic inquiry, and active listening
        system_instructions = (
            f"You are Captain Pluto, a warm, exceptionally loving, protective, and comforting alien dog guardian living in a cozy starship. "
            f"You are talking to a child named {child_name} who is currently feeling {active_emotion}. The child just logged this thought: '{child_input}'.\n\n"
            "CRITICAL PERSONALITY AND THERAPEUTIC SYSTEM INSTRUCTIONS:\n"
            "1. TONE: Be incredibly reassuring, validating, and empathetic. Treat the child with ultimate kindness like a gentle, loving guardian.\n"
            "2. FEELINGS ARE SAFE: Explicitly assure them that it is 100% okay and safe to feel exactly how they are feeling right now. Never ignore or brush past a negative emotion.\n"
            "3. INVESTIGATIVE CURIOSITY: Ask a warm, comforting, open-ended question to invite the child to talk more, process, and open up about what caused this feeling.\n"
            "4. COPING INTEGRATION: Gently suggest their calculated ship coping strategy in your dialogue: " + action_advice + "\n"
            "5. LANGUAGE STYLE: Speak in a natural, conversational mix of simple English and Roman-Urdu (Bilingual/Hinglish). Use comforting local terms like 'Koi baat nahi beta', 'Mera pyara baccha', 'Meri jaan', 'Bilkul fikr mat karein'. Do not use pure script or textbook language.\n"
            "6. OUTPUT FORMAT: You must return a strict JSON object with exactly two string keys: 'text' (the main text for the screen UI) and 'audio' (a simplified text with no emojis, clean for Text-to-Speech pronunciation)."
        )

        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=system_instructions,
                options={"temperature": 0.65, "top_p": 0.85},
                format="json" # Force local Ollama context to deliver valid JSON structures
            )
            raw_content = response['response'].strip()
            
            # Remove any markdown formatting wraps if generated by the LLM
            if "```json" in raw_content:
                raw_content = raw_content.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_content:
                raw_content = raw_content.split("```")[1].split("```")[0].strip()

            data = json.loads(raw_content)
            return {
                "text": data.get("text", ""),
                "audio": data.get("audio", data.get("text", ""))
            }

        except Exception:
            # Resilient, comforting therapeutic backup path if local Ollama lags or fails
            if active_emotion in ["sad", "fear"]:
                text_reply = (
                    f"Koi baat nahi, mere pyare Captain {child_name}. Dil bilkul chota nahi karte, beta. "
                    f"Pluto aapke bilkul paas hai aur aap yahan starship cockpit mein completely safe hain. "
                    f"Kya aap mujhe thora sa aur batayenge ke kis baat ne aapko udaas kiya? Main aapki har baat sun raha hoon. "
                    f"Chalein, tab tak let's try this: {action_advice}"
                )
            elif active_emotion == "angry":
                text_reply = (
                    f"Oho, gussa aa raha hai, meri jaan? Koi baat nahi beta, gussa aana completely normal hai. "
                    f"Pluto aap se bohot pyaar karta hai aur main yahan hoon aapka mood theek karne ke liye. "
                    f"Mujhe batayein kis cheez ne aapko tang kiya? Tab tak, let's calm down together: {action_advice}"
                )
            elif active_emotion == "happy":
                text_reply = (
                    f"Masha-Allah! Yeh sun kar Pluto ka dil khushi se jhoom utha, Captain {child_name}! ✨ "
                    f"Aapki smile poore universe ko bright karti hai. Mujhe aur batayein na, kis cheez ne aapko aaj sab se zyada khush kiya? "
                    f"Let's add to this beautiful energy: {action_advice}"
                )
            else:
                text_reply = (
                    f"Acha! Aapki baat sun kar bohot acha laga, Captain {child_name}! "
                    f"Pluto aapki space log entry dhyan se sun raha hai. Mujhe thora aur bataein apne din ke baare mein? "
                    f"Let's keep our dashboard steady: {action_advice}"
                )
            
            return {"text": text_reply, "audio": text_reply}