import cv2
from datetime import datetime
import os
import time


def in_out():

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Camera not accessible")
        return

    #  folders
    os.makedirs("visitors/in", exist_ok=True)
    os.makedirs("visitors/out", exist_ok=True)

    prev_gray = None
    last_event_time = 0
    direction = None

    in_count = 0
    out_count = 0

    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480

    print("✅ IN-OUT Detection Started (ESC to exit)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        frame = cv2.flip(frame, 1)

        #  PREPROCESS 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if prev_gray is None:
            prev_gray = gray
            continue

        # MOTION DETECTION 
        diff = cv2.absdiff(prev_gray, gray)

        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(
            thresh.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        pos_x = None

        # OBJECT DETECTION 
        if contours:
            max_cnt = max(contours, key=cv2.contourArea)

            if cv2.contourArea(max_cnt) > 2500:
                x, y, w, h = cv2.boundingRect(max_cnt)
                pos_x = x + w // 2

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "PERSON DETECTED", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # VIRTUAL LINES 
        left_line = int(FRAME_WIDTH * 0.3)
        right_line = int(FRAME_WIDTH * 0.7)

        # ENTRY LINE
        cv2.line(frame, (left_line, 0), (left_line, FRAME_HEIGHT), (255, 255, 0), 2)
        cv2.putText(frame, "ENTRY", (left_line - 40, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # EXIT LINE
        cv2.line(frame, (right_line, 0), (right_line, FRAME_HEIGHT), (0, 255, 255), 2)
        cv2.putText(frame, "EXIT", (right_line - 30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        #  DIRECTION LOGIC 
        if pos_x is not None:

            if direction is None:
                if pos_x > right_line:
                    direction = "right"
                elif pos_x < left_line:
                    direction = "left"

            else:
                current_time = time.time()

                #  IN
                if direction == "right" and pos_x < left_line:
                    if current_time - last_event_time > 2:

                        in_count += 1
                        print(f"➡️ IN | Total: {in_count}")

                        filename = f"visitors/in/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
                        cv2.imwrite(filename, frame)

                        last_event_time = current_time
                        direction = None

                #  OUT
                elif direction == "left" and pos_x > right_line:
                    if current_time - last_event_time > 2:

                        out_count += 1
                        print(f"⬅️ OUT | Total: {out_count}")

                        filename = f"visitors/out/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
                        cv2.imwrite(filename, frame)

                        last_event_time = current_time
                        direction = None

        #  DASHBOARD TEXT 
        cv2.putText(frame, f"IN: {in_count}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.putText(frame, f"OUT: {out_count}", (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        #  DISPLAY 
        cv2.imshow("IN-OUT Detection (AI Surveillance)", frame)

        prev_gray = gray

        if cv2.waitKey(1) & 0xFF == 27:
            break

        time.sleep(0.01)

    cap.release()
    cv2.destroyAllWindows()