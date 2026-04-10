import cv2
import time
import os

# folder create (ek baar hi)
os.makedirs("captures", exist_ok=True)

def save_capture(frame, prefix="cap"):
    try:
        timestamp = int(time.time())
        filename = f"captures/{prefix}_{timestamp}.jpg"

        cv2.imwrite(filename, frame)

        print(f"[SAVED] {filename}")

        return filename

    except Exception as e:
        print("[ERROR] Saving failed:", e)
        return None