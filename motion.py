import cv2
import time
import os
import winsound


def motion_detect():

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Camera not working")
        return

    #  FOLDER 
    os.makedirs("motion_videos", exist_ok=True)

    #  INIT
    ret, prev = cap.read()
    if not ret:
        return

    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (5, 5), 0)

    recording = False
    out = None
    start_time = 0
    last_motion_time = 0

    print("🚀 Smart Motion + Recording Started")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        #  MOTION 
        diff = cv2.absdiff(prev_gray, gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        contours = [c for c in contours if cv2.contourArea(c) > 1500]

        #  MOTION FOUND 
        if len(contours) > 0:

            last_motion_time = time.time()

            # START RECORDING
            if not recording:
                filename = f"motion_videos/{int(time.time())}.avi"

                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

                winsound.Beep(1500, 200)

                recording = True
                start_time = time.time()

                print("🎥 Recording Started:", filename)

        #  STOP RECORD 
        if recording and (time.time() - last_motion_time > 3):

            recording = False
            out.release()

            print(" Recording Stopped")

        #  WRITE VIDEO 
        if recording:
            out.write(frame)

            #  Blinking REC
            if int(time.time() * 2) % 2 == 0:
                cv2.putText(frame, "REC", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 3)

            #  Timer
            duration = int(time.time() - start_time)
            cv2.putText(frame, f"{duration}s", (100, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 255), 2)

        #  Date + Time
        timestamp = time.strftime("%d-%m-%Y %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 470),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 2)

        #  DISPLAY 
        cv2.imshow("SMART MOTION AI", frame)

        prev_gray = gray

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()