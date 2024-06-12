import serial
import sys
import lib1785b
import time

port = "/dev/ttyUSB0"
ser = serial.Serial(port) # "/dev/ttyUSB0", "com2" etc...
#should define the serial as the port connected to ALDO supply
lib1785b.remoteMode(True, ser)
# v0 = float(lib1785b.readAll(ser)['vset'])
# stepVolt(ser, v0, 0, t=1, dt=0.25) #sets voltage to 0 on startup

def stepVolt(ser, v0, v1, t=5, dt=0.25):
    nt = t/dt
    dv = (v1-v0)/nt
    newV = v0
    for i in range(int(nt)):
        newV = newV + dv
        lib1785b.volt(newV, ser)
        time.sleep(dt)
    lib1785b.volt(newV, ser)

def waitUntilVolt(volt):
    while not abs(float(lib1785b.readAll(ser)['vset']) - volt) <= 0.2:
        time.sleep(0.05)
    
def volt(voltage, t=5):
    dt = 0.25 #length of time for each step in seconds
    data = lib1785b.readAll(ser)
    v0 = float(data['vset'])
    if t == 0:
        t = dt
    v1 = float(voltage)
    if v1 > 0:
        lib1785b.outputOn(True, ser)
    if v1 > 48:
        print("ALDO voltage is limited at 48.")
    elif v1 == v0:
        lib1785b.volt(v0, ser)
    elif v1 <= 0:
        print("Setting ALDO voltage to 0V")
        stepVolt(ser, v0, v1, t, dt)
        waitUntilVolt(0)
        lib1785b.outputOn(False, ser)
    else:
        print("Setting ALDO voltage to " + str(voltage) + "V")
        lib1785b.outputOn(True, ser)
        stepVolt(ser, v0, v1, t, dt)

def onOff(on, t=5): #on == True for turning supply on, False for turning off
    v0 = float(lib1785b.readAll(ser)['vset'])
    isOn = ~lib1785b.readAll(ser)['output']
    if (on and isOn) or (off and not isOn):
        #already in desired state
        time.sleep(0.01)
    elif (on and not isOn):
        print("Powering on ALDOs")
        lib1785b.volt(0, ser)
        lib1785b.outputOn(True, ser)
        stepVolt(ser, 0, v0, t, dt=0.25)
    elif (off and isOn):
        print("Powering down ALDOs")
        stepVolt(ser, v0, 0, t, dt=0.25)
        lib1785b.outputOn(False, ser)
