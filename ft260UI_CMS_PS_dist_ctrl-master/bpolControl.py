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

ser1 = serial.Serial("/dev/ttyUSB0", timeout=0.1) #Note that this uses the same port as the ALDOs.
# This has to be fixed before trying to control both simultaneously.
#ser2 = serial.Serial("/dev/ttyUSB0", timeout=0.1) #This port is for the second bPOL12V power supply. It should be changed when a new USB port is made available

def volt(voltage, t=5):
    args = sys.argv
    dt = 0.25
    v1 = float(voltage)
    v0 = float(lib1685b.getSettings(ser1)[0])

    print("Setting bPOL voltage to " + str(v1))
    if v1 == 0:
        stepVolt(ser1, v0, 1, t, dt)
#        stepVolt(ser2, v0, 1, t, dt)
        time.sleep((v0+0.01) / 6)
        lib1685b.onOff(ser1, 1)
#        lib1685b.onOff(ser2, 1)
    elif v1 == v0:
        lib1685b.onOff(ser1, 0)
#        lib1685b.onOff(ser2, 0)
    elif v1 > 12:
        print("bPOL voltage cannot exceed 12V.")
    else:
        lib1685b.onOff(ser1, 0)
#        lib1685b.onOff(ser2, 0)
        stepVolt(ser1, v0, v1, t, dt)
#        stepVolt(ser2, v0, v1, t, dt)

#temp = sys.argv
#volt(float(temp[1]), float(temp[2]))
