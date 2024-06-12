import serial
import sys
import lib1785b
import time

def stepVolt(ser, v0, v1, t=5, dt=0.25):
    nt = t/dt
    dv = (v1-v0)/nt
    newV = v0
    for i in range(int(nt)):
        newV = newV + dv
        lib1785b.volt(newV, ser)
        time.sleep(dt)
    lib1785b.volt(newV, ser)

ser = serial.Serial("/dev/ttyUSB0") # "/dev/ttyUSB0", "com2" etc...
#should define the serial as the port connected to ALDO supply
lib1785b.remoteMode(True, ser)

def volt(voltage, t=5):
    dt = 0.25 #length of time for each step in seconds
    data = lib1785b.readAll(ser)
    v0 = float(data['vset'])
    if t == 0:
        t = dt
    v1 = float(voltage)
    if v1 > 50:
        print("ALDO voltage is limited at 50.")
    elif v1 == v0:
        lib1785b.volt(v0, ser)
    elif v1 == 0:
        print("Setting voltage to 0V")
        stepVolt(ser, v0, v1, t, dt)
        time.sleep(1)
        lib1785b.outputOn(False, ser)
    else:
        print("Setting voltage to " + str(voltage) + "V")
        lib1785b.outputOn(True, ser)
        stepVolt(ser, v0, v1, t, dt)

def off(t=5):
    print("Powering down aldos")
    v0 = float(lib1785b.readAll(ser)['vset'])
    stepVolt(ser, v0, 0, t, dt=0.25)
    lib1785b.outputOn(False, ser)