import cv2
import time
from utils import save_capture


def ai_person_detect():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Camera error")
        return

    #  HOG Person Detector
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    last_capture_time = 0   

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        #  Resize for speed
        frame = cv2.resize(frame, (640, 480))

        #  Detection (optimized params)
        boxes, weights = hog.detectMultiScale(
            frame,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05
        )

        # Time display
        t = time.strftime("%H:%M:%S")
        cv2.putText(
            frame, t, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 255, 0), 2
        )

        detected = False  

        for (x, y, w, h) in boxes:

            detected = True

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "Person",
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        #  Capture only once in few seconds
        if detected:
            current_time = time.time()

            if current_time - last_capture_time > 3:   # 3 sec cooldown
                save_capture(frame)
                print("[📸 PERSON DETECTED]")
                last_capture_time = current_time

        cv2.imshow("AI Person Detect", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()