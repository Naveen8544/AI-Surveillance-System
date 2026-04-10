import time
import winsound   

def alert():

    t = time.strftime("%Y-%m-%d %H:%M:%S")

    print(f"🚨 INTRUDER DETECTED at {t}")

    #  Beep sound
    try:
        winsound.Beep(1500, 500)
    except:
        pass