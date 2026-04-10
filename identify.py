import cv2
import os
import time


def maincall(person_name):   

    if not person_name:
        print("❌ No name entered")
        return

    save_path = f"persons/{person_name}"
    os.makedirs(save_path, exist_ok=True)

    time.sleep(1)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Camera busy")
        return

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    count = len(os.listdir(save_path))

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, person_name, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Face Capture", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 32 and len(faces) > 0:
            for (x, y, w, h) in faces:
                face = frame[y:y+h, x:x+w]

                filename = f"{save_path}/img_{count}.jpg"
                cv2.imwrite(filename, face)

                print("✅ Saved:", filename)
                count += 1

        elif key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()