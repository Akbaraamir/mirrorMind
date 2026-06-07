# Mirror Mind 🧠✨
> A next-generation, emotionally aware cognitive companion for children.

Mirror Mind is an innovative, privacy-first desktop application designed to serve as a safe digital space for children to express themselves, interact, and grow. By seamlessly blending real-time computer vision with local conversational intelligence, the platform acts as an empathetic digital partner that adapts dynamically to a child's emotional state.

---

## 🚀 Key Features

*   **🔒 COPPA-Compliant Gatekeeping:** A secure entrance portal utilizing parental verification and consent mechanisms to keep all user profile settings fully locked down.
*   **👁️ Real-Time Affective Computing:** Leverages the **DeepFace** library to actively process camera inputs, decoding facial landmarks into granular emotional states (e.g., Happy, Sad, Neutral).
*   **⏱️ Smart 4-Second Thresholding:** Features a custom algorithmic filter that ensures an emotional expression is held continuously for at least 4 seconds before triggering an AI response—eliminating accidental micro-expression glitches or false tracking triggers.
*   **🤖 Local, Private AI Conversations:** Powered by an advanced, localized language model via **Ollama** running the custom companion agent, **Pluto**. Pluto delivers natural, supportive, human-like dialogue without sending private user data to the cloud.

---

## 🛠️ Architecture & Tech Stack

Mirror Mind splits the user interface and processing load into a highly synchronized dual-track architecture:

*   **Frontend UI:** Python-based GUI (Tkinter/PyQt framework) optimizing a clean, split-screen layout—visual emotional tracking telemetry on the left, interactive chat feed on the right.
*   **Computer Vision Backend:** `DeepFace` framework mapped over open-source web-capture interfaces.
*   **Local LLM Host:** `Ollama` running customized contextual personas.
*   **Data Tier:** Secure local serialization via lightweight JSON structures (`user_profiles.json`) and session historical logging (`user_history.csv`).

---

## 📁 Repository Structure

```text
├── brain.py                  # Core AI brain and prompt orchestration
├── mirrormind_app.py         # Primary application lifecycle and entry point
├── mirrormind_ui.py          # Dashboard layouts and UI thread bindings
├── parent_view.py            # Parental analytics dashboard metrics
├── parental_consent.py       # COPPA authentication logic
├── perception.py             # DeepFace emotion capture and 4-second filter engine
├── reflection_engine.py      # Dialog-mapping and emotional contextualizer
├── space_passport_config.json # App configurations and profile states
├── user_profiles.json        # Encrypted/secured child baseline profile settings
└── user_history.csv          # Local historical session tracking data
