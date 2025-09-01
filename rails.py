import serial
import time
import re
import threading

LEFT_PORT = 'COM5'
RIGHT_PORT = 'COM9'
OUT_PORT = 'COM12'
BAUDRATE = 115200
scaler = 95  # Adjust this value as needed

ser_left = serial.Serial(LEFT_PORT, BAUDRATE, timeout=0.1)
ser_right = serial.Serial(RIGHT_PORT, BAUDRATE, timeout=0.1)
ser_out = serial.Serial(OUT_PORT, BAUDRATE, timeout=0.1, write_timeout=1)

time.sleep(2)
ser_out.reset_input_buffer()
ser_out.write(b'$X\n')  # clear any locks

def send(cmd):
    ser_out.write(cmd.encode('utf-8'))
    ser_out.flush()
    time.sleep(0.05)

send("\r\n\r\n")
time.sleep(2)
ser_out.reset_input_buffer()
send("G21\nG90\n")
send("$X\n")

def move_x(pos):
    print(f"Moving X to {pos}")
    send(f"G0 X{pos}\n")

def move_y(pos):
    print(f"Moving Y to {pos}")
    send(f"G0 Y{pos}\n")

def clear_buffer(ser):
    while ser.in_waiting:
        _ = ser.readline()

zone_pattern = re.compile(r'Zone\s+(-?\d+)', re.IGNORECASE)

def listen_left():
    while True:
        line = ser_left.readline().decode('utf-8', errors='ignore').strip()
        if line and line != "wait":
            print(f"[LEFT] Received: {line}")
            match = zone_pattern.search(line)
            if match:
                print(f"[LEFT] Moving to: {line}")
                val = int(match.group(1))
                move_x(val/scaler)
                clear_buffer(ser_left)

def listen_right():
    while True:
        line = ser_right.readline().decode('utf-8', errors='ignore').strip()
        if line and line != "wait":
            print(f"[Right] Received: {line}")
            match = zone_pattern.search(line)
            if match:
                print(f"[RIGHT] Moving to: {line}")
                val = int(match.group(1))
                move_y(val/scaler)
                clear_buffer(ser_right)

print("Listening for 'Zone n' on left and right ports...")

try:
    t_left = threading.Thread(target=listen_left, daemon=True)
    t_right = threading.Thread(target=listen_right, daemon=True)
    t_left.start()
    t_right.start()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting.")
finally:
    ser_left.close()
    ser_right.close()
    ser_out.close()
