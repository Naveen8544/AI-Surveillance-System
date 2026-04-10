import tkinter as tk
from PIL import Image, ImageTk
import threading
import tkinter.simpledialog as sd

from motion import motion_detect
from rect_noise import rect_noise
from record import record
from ai_detect import ai_person_detect
from identify import maincall
from find_motion import find_motion
from in_out import in_out
from ultra_plate_ai import ultra_number_plate


#  GLOBAL CAMERA LOCK 
running = False


#  SAFE THREAD RUN 
def run_thread(func):
    global running

    if running:
        print(" Camera already in use")
        return

    running = True

    def wrapper():
        global running
        try:
            func()
        except Exception as e:
            print("❌ Error:", e)
        finally:
            running = False

    threading.Thread(target=wrapper, daemon=True).start()


#  IDENTIFY 
def identify_wrapper():
    global running

    if running:
        print(" Camera already in use")
        return

    name = sd.askstring("Input", "Enter person name:")
    if name:
        run_thread(lambda: maincall(name))


#  VEHICLE AI
def vehicle_wrapper():
    global running

    if running:
        print(" Camera already in use")
        return

    import cv2

    running = True

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print(" Camera error")
        running = False
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = ultra_number_plate(frame)

            cv2.imshow("🚗 Vehicle AI", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    except Exception as e:
        print(" Vehicle Error:", e)

    finally:
        cap.release()
        cv2.destroyAllWindows()
        running = False


# WINDOW 
window = tk.Tk()
window.title("AI Surveillance Pro Dashboard")
window.geometry("1000x600")
window.config(bg="#202020")


#  TITLE 
top = tk.Frame(window, bg="#111111", height=60)
top.pack(fill="x")

title = tk.Label(
    top,
    text="AI SURVEILLANCE PRO DASHBOARD",
    bg="#111111",
    fg="white",
    font=("Arial", 18, "bold")
)
title.pack(pady=10)


#  SCROLLABLE SIDEBAR 
sidebar_container = tk.Frame(window, bg="#181818")
sidebar_container.pack(side="left", fill="y")

canvas = tk.Canvas(sidebar_container, bg="#181818", highlightthickness=0)
scrollbar = tk.Scrollbar(sidebar_container, orient="vertical", command=canvas.yview)

scrollable_frame = tk.Frame(canvas, bg="#181818")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="y", expand=True)
scrollbar.pack(side="right", fill="y")


# Mouse scroll
def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)


#  MAIN 
main = tk.Frame(window, bg="#202020")
main.pack(fill="both", expand=True)


#  ICON LOAD 
def load_icon(name):
    try:
        img = Image.open("icons/" + name)
        img = img.resize((35, 35))
        return ImageTk.PhotoImage(img)
    except:
        print("Icon not found:", name)
        return None


#  ICONS 
icon_monitor = load_icon("camera.png")
icon_motion = load_icon("motion.png")
icon_record = load_icon("record.png")
icon_ai = load_icon("ai.png")
icon_exit = load_icon("exit.png")
icon_face = load_icon("face.png")
icon_rect = load_icon("rect.png")
icon_inout = load_icon("inout.png")
icon_vehicle = load_icon("vehicle.png")


#  BUTTON 
def side_btn(text, icon, func, use_thread=True):

    if use_thread:
        cmd = lambda: run_thread(func)
    else:
        cmd = func

    btn = tk.Button(
        scrollable_frame,
        text="  " + text,
        image=icon,
        compound="left",
        command=cmd,
        bg="#181818",
        fg="white",
        font=("Arial", 12, "bold"),
        relief="flat",
        padx=10,
        pady=10,
        anchor="w"
    )

    btn.pack(fill="x", pady=5)


#  BUTTONS 
side_btn("Monitor", icon_monitor, find_motion)
side_btn("Motion", icon_motion, motion_detect)
side_btn("Rectangle", icon_rect, rect_noise)
side_btn("Record", icon_record, record)
side_btn("AI Detect", icon_ai, ai_person_detect)


side_btn("Vehicle AI", icon_vehicle, vehicle_wrapper, use_thread=False)

side_btn("Identify", icon_face, identify_wrapper, use_thread=False)

side_btn("In Out", icon_inout, in_out)

side_btn("Exit", icon_exit, window.destroy, use_thread=False)


#  CENTER TEXT 
label = tk.Label(
    main,
    text="Welcome to AI Surveillance System",
    bg="#202020",
    fg="white",
    font=("Arial", 20)
)
label.pack(pady=150)


window.mainloop()