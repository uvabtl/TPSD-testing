import serial
import time

ser = serial.Serial()
ser.baudrate = 9600
ser.port = "/dev/ttyUSB0"
ser.timeout = 1
print(ser)
ser.open()
print(ser.is_open)
ser.write("VOLT120\r".encode())
print("Wrote")
resp = ser.read(20)
print(resp)
print("read")
ser.write("GETS\r".encode())
print(ser.read(20))
ser.write("GETD\r".encode())
print(ser.read(16))
ser.close()
