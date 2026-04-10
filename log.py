import time
import os

# ensure log file exists
if not os.path.exists("log.txt"):
    open("log.txt", "w").close()


def write_log(msg):
    try:
        t = time.strftime("%Y-%m-%d %H:%M:%S")

        with open("log.txt", "a") as f:
            f.write(f"{t} - {msg}\n")

        print(f"[LOG] {msg}")

    except Exception as e:
        print("[ERROR] Log failed:", e)