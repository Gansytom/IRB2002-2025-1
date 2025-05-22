import serial
import csv

ser = serial.Serial('/dev/ttyACM0', 115200)
output_file = open("gps_single_log.csv", "w", newline='')
writer = csv.writer(output_file)

writer.writerow(["lat", "lon"])

try:
    while True:
        line = ser.readline().decode().strip()
        if line.count(",") == 1 and "lat" not in line:
            writer.writerow(line.split(","))
except KeyboardInterrupt:
    print("Captura terminada por el usuario.")
    output_file.close()
    ser.close()
