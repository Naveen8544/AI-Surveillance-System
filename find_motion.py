import cv2
from spot_diff import spot_diff
import time
import os
import winsound


def find_motion():

    motion_detected = False
    start_time = None

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Camera error")
        return

    print("⏳ Camera stabilizing...")
    time.sleep(2)

    # create folder
    os.makedirs("motion_captures", exist_ok=True)

    ret, frame1 = cap.read()
    if not ret:
        cap.release()
        return

    prev_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (5, 5), 0)

    while True:

        ret, frame2 = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        diff = cv2.absdiff(prev_gray, gray)

        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        contours = [c for c in contours if cv2.contourArea(c) > 1500]

        #  MOTION 
        if len(contours) > 0:

            cv2.putText(thresh, "🚨 MOTION DETECTED", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)

            if not motion_detected:
                motion_detected = True
                start_time = time.time()

                # SOUND
                winsound.Beep(1500, 300)

        else:

            cv2.putText(thresh, "NO MOTION", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)

               # EVENT END 
            if motion_detected and (time.time() - start_time > 2):

                print("✅ Motion event completed")

                result = spot_diff(frame1, frame2)

                if result == 0:
                    print("ℹ️ False motion")
                else:
                    print("🚨 REAL MOTION DETECTED")

                    #  SAVE IMAGE
                    filename = f"motion_captures/{int(time.time())}.jpg"
                    cv2.imwrite(filename, frame2)
                    print("📸 Saved:", filename)

                    #  ALERT
                    winsound.Beep(2000, 500)

                # reset
                motion_detected = False
                start_time = None

        #  DRAW BOX 
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame2, (x, y), (x+w, y+h), (0, 255, 0), 2)

        #  DISPLAY 
        cv2.imshow("SMART MOTION AI", frame2)

        prev_gray = gray
        frame1 = frame2

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()