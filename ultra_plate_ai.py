import cv2
from ultralytics import YOLO
import pytesseract
import pandas as pd
import time
import os
import winsound

#  TESSERACT 
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#  LOAD MODEL 
model = YOLO("yolov8n.pt")

#  FOLDERS 
os.makedirs("captures", exist_ok=True)

if not os.path.exists("logs.csv"):
    pd.DataFrame(columns=["Time", "Vehicle", "Plate"]).to_csv("logs.csv", index=False)

#  GLOBAL 
last_plate = ""
last_time = 0


# CLEAN TEXT 
def clean_text(text):
    return "".join(c for c in text if c.isalnum())


#  SAVE LOG
def save_log(vehicle, plate):
    try:
        new = {
            "Time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Vehicle": vehicle,
            "Plate": plate
        }

        df = pd.read_csv("logs.csv")
        df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        df.to_csv("logs.csv", index=False)

    except Exception as e:
        print("[LOG ERROR]", e)


#  MAIN AI FUNCTION 
def ultra_number_plate(frame):
    global last_plate, last_time

    try:
        frame = cv2.resize(frame, (640, 480))

        results = model(frame, conf=0.5, verbose=False)

        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:

                conf = float(box.conf[0])
                if conf < 0.5:
                    continue

                cls = int(box.cls[0])
                label = model.names[cls]

                #  Only vehicles
                if label not in ["car", "bus", "truck", "motorbike"]:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                #  SAFE CROP 
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(frame.shape[1], x2)
                y2 = min(frame.shape[0], y2)

                vehicle = frame[y1:y2, x1:x2]

                if vehicle.size == 0:
                    continue

                #  SMART ROI 
                h, w = vehicle.shape[:2]

                plate_roi = vehicle[
                    int(h * 0.55):int(h * 0.9),
                    int(w * 0.2):int(w * 0.8)
                ]

                if plate_roi.size == 0:
                    continue

                #  PREPROCESS 
                gray = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
                gray = cv2.bilateralFilter(gray, 11, 17, 17)

                thresh = cv2.adaptiveThreshold(
                    gray,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    11,
                    2
                )

                #  OCR 
                text = pytesseract.image_to_string(
                    thresh,
                    config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                )

                plate = clean_text(text)

                #  DRAW 
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label.upper(), (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                #  FILTER 
                if plate != "" and len(plate) >= 7:

                    current_time = time.time()

                    if plate != last_plate or (current_time - last_time > 3):

                        #  Beep
                        try:
                            winsound.Beep(1000, 200)
                        except:
                            pass

                        last_plate = plate
                        last_time = current_time

                        #  DISPLAY 
                        cv2.putText(frame, plate, (x1, y2 + 25),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                        #  SAVE 
                        filename = f"captures/{int(time.time())}.jpg"
                        cv2.imwrite(filename, frame)

                        save_log(label, plate)

                        print("🚗 DETECTED:", plate)

    except Exception as e:
        print("❌ ERROR:", e)

    return frame