import cv2
from deepface import DeepFace
import os

# Bridge for TensorFlow 2.21+
os.environ['TF_USE_LEGACY_KERAS'] = '1'

# 0 is usually the built-in camera
cap = cv2.VideoCapture(0)

print("--- MirrorMind Perception Layer Active ---")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        # analyze the 'State' (S) of the user
        results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        emotion = results[0]['dominant_emotion']
        
        # Draw the emotion on the screen for the "Mirror" effect
        cv2.putText(frame, f"Emotion: {emotion}", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('MirrorMind', frame)
    except:
        pass

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()