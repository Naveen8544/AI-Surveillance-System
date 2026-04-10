import cv2
from skimage.metrics import structural_similarity
from datetime import datetime
import beepy
import os


def spot_diff(frame1, frame2):

    os.makedirs("stolen", exist_ok=True)

    #  Grayscale safe conversion
    g1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY) if len(frame1.shape) == 3 else frame1
    g2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY) if len(frame2.shape) == 3 else frame2

    #  Blur (noise reduce)
    g1 = cv2.GaussianBlur(g1, (5, 5), 0)
    g2 = cv2.GaussianBlur(g2, (5, 5), 0)

    #  SSIM compare
    score, diff = structural_similarity(g2, g1, full=True)

    print("📊 Image similarity:", round(score, 4))

    #  IMPORTANT FILTER (false detection fix)
    if score > 0.97:
        print("✅ Ignore (Too similar)")
        return 0

    diff = (diff * 255).astype("uint8")

    
    thresh = cv2.threshold(diff, 0, 255,
                           cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    #  Morphology (noise clean)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    #  Contours
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    #  Strong filter (reduce false positives)
    contours = [c for c in contours if cv2.contourArea(c) > 1500]

    if len(contours) == 0:
        print("✅ No significant change")
        return 0

    #  Draw bounding boxes
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

    #  Alert
    try:
        beepy.beep(sound=4)
    except:
        pass

    #  Save evidence
    filename = "stolen/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
    cv2.imwrite(filename, frame1)

    #  Show result (non-blocking)
    cv2.imshow("Difference", thresh)
    cv2.imshow("Detected Change", frame1)
    cv2.waitKey(1)

    print("🚨 REAL CHANGE DETECTED & SAVED")

    return 1