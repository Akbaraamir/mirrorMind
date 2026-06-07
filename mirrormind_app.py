# mirrormind_app.py
from mirrormind_ui import MirrorMindApp
import os

if __name__ == "__main__":
    # Ensure legacy ML bridges are ready
    os.environ['TF_USE_LEGACY_KERAS'] = '1'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    # Fire up the professional space console
    app = MirrorMindApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()