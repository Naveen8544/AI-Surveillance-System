import cv2
import time
import os
import winsound

drawing = False
ix, iy = -1, -1
rect = None


def draw_rect(event, x, y, flags, param):
    global ix, iy, drawing, rect

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            rect = (ix, iy, x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect = (ix, iy, x, y)


def rect_noise():
    global rect

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Camera error")
        return

    os.makedirs("roi_captures", exist_ok=True)

    cv2.namedWindow("SMART ROI MOTION")
    cv2.setMouseCallback("SMART ROI MOTION", draw_rect)

    prev_gray = None
    last_save_time = 0

    print("👉 Drag mouse to select region")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        display = frame.copy()

        if rect:
            x1, y1, x2, y2 = rect

            
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])

            #  ignore too small ROI
            if abs(x2 - x1) < 50 or abs(y2 - y1) < 50:
                cv2.imshow("SMART ROI MOTION", display)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
                continue

            roi = frame[y1:y2, x1:x2]

            if roi.size == 0:
                continue

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)

            #  size mismatch crash
            if prev_gray is None or prev_gray.shape != gray.shape:
                prev_gray = gray
                continue

            diff = cv2.absdiff(prev_gray, gray)

            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            thresh = cv2.dilate(thresh, None, iterations=2)

            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            contours = [c for c in contours if cv2.contourArea(c) > 800]

            #  MOTION 
            if len(contours) > 0:

                cv2.putText(display, "🚨 ROI MOTION", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                for c in contours:
                    cx, cy, cw, ch = cv2.boundingRect(c)

                    cv2.rectangle(display,
                                  (x1 + cx, y1 + cy),
                                  (x1 + cx + cw, y1 + cy + ch),
                                  (0, 0, 255), 2)

                #  cooldown fix
                if time.time() - last_save_time > 2:
                    winsound.Beep(1500, 200)

                    filename = f"roi_captures/{int(time.time())}.jpg"

                    #  SAVE CHECK
                    success = cv2.imwrite(filename, frame)

                    if success:
                        print("📸 ROI Saved:", filename)
                    else:
                        print("❌ Save failed")

                    last_save_time = time.time()

            prev_gray = gray

            # draw rectangle
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.imshow("SMART ROI MOTION", display)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()