import serial

ser = serial.Serial('COM7', 9600)
while True:
    data = ser.readline().decode('utf-8').strip()
    print("Received:", data)