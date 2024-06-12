import serial
import sys
import time
import lib1685b

def stepVolt(ser, v0, v1, t=5, dt=0.25):
    nt = t/dt
    dv = (v1-v0)/nt
    newV = v0
    for i in range(int(nt)):
        newV = newV + dv
        lib1685b.setVoltage(ser, newV)
        time.sleep(dt)
    lib1685b.setVoltage(ser, v1)

ser = serial.Serial("/dev/ttyUSB0") #Note that this uses the same port as the ALDOs.
# This has to be fixed before trying to control both simultaneously.
ser.timeout = 0.1

def volt(voltage, t=5):
    args = sys.argv
    dt = 0.25
    v1 = float(voltage)
    v0 = float(lib1685b.getSettings(ser)[0])

    print("Setting TEC voltage to " + str(v1))
    if v1 == 0:
        stepVolt(ser, v0, 1, t, dt)
        time.sleep((v0+0.01) / 6)
        lib1685b.onOff(ser, 1)
    elif v1 == v0:
        lib1685b.onOff(ser, 0)
    elif v1 > 36:
        print("TEC voltage cannot exceed 36V.")
    else:
        lib1685b.onOff(ser, 0)
        stepVolt(ser, v0, v1, t, dt)

#temp = sys.argv
#volt(float(temp[1]), float(temp[2]))

def off(t=5):
    v0 = float(lib1685b.getSettings(ser)[0])
    print("Powering down tecs")
    stepVolt(ser, v0, 1, t, dt=0.25)
    time.sleep((v0+0.01)/4)
    lib1685b.onOff(ser, 1)