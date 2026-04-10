import csv
from datetime import datetime

def save_log(vehicle, plate):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([time_now, vehicle, plate])

    print("Log Saved:", time_now, vehicle, plate)