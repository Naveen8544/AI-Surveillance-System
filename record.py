import cv2
from datetime import datetime
import os
import time

def record():

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Camera error")
        return

    os.makedirs("recordings", exist_ok=True)

    filename = f"recordings/{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"

    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    width = int(cap.get(3))
    height = int(cap.get(4))

    out = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))

    print("🎥 Recording started...")
    print("Saving to:", filename)

    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        #  TIMER 
        elapsed = int(time.time() - start_time)

        hrs = elapsed // 3600
        mins = (elapsed % 3600) // 60
        secs = elapsed % 60

        timer = f"{hrs:02}:{mins:02}:{secs:02}"

        #  BLINKING REC 
        if secs % 2 == 0:
            cv2.putText(frame, "REC ●", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        #  TIMER TEXT 
        cv2.putText(frame, timer, (150, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        #  DATE + TIME 
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        cv2.putText(frame, now, (20, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        # SAVE FRAME
        out.write(frame)

        cv2.imshow("Recording (ESC to stop)", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("✅ Recording saved successfully")