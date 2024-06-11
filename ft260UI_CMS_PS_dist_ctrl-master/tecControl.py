import serial
import sys
import time
import lib1685b

ser = serial.Serial("/dev/ttyUSB0") #Note that this uses the same port as the ALDOs.
# This has to be fixed before trying to control both simultaneously.
ser.timeout = 0.1

args = sys.argv
lib1685b.getMaxVoltCurr(ser)

print("Setting TEC voltage to " + args[1])

lib1685b.setVoltage(ser, float(args[1]))
