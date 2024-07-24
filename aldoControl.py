import serial
import serial.tools.list_ports
import sys
import lib1785b
import time
import ft

#port = "/dev/ttyUSB0"
#ser = serial.Serial(port) # "/dev/ttyUSB0", "com2" etc...
#should define the serial as the port connected to ALDO supply
#lib1785b.remoteMode(True, ser)

def find_ALDO(vidTarget, pidTarget):
    for portRead in serial.tools.list_ports.comports():
        if portRead[2] != 'n/a':
            vidpid = portRead[2].split(' ')[1].split('=')[1]
            vid = hex(int("0x"+vidpid.split(':')[0], 16))
            pid = hex(int("0x"+vidpid.split(':')[1], 16))
            if vid==hex(vidTarget) and pid==hex(pidTarget):
                try:
                    port=portRead[0]
                    ser = serial.Serial(port)
                    #print(ser)
                    ser.timeout = 0.1
                    id = lib1785b.readID(ser)
                    if id["model"] == '682':
                        #print("Found")
                        return ser
                    else:
                        #print("closed")
                        ser.close()
                except:
                    #print("Close")
                    ser.close()
                    print(ser.name)
                    pass
    #print("Closed")
    ser.close()
    raise Exception("Could not find ALDO PS")

vidTarget = 0x067b
pidTarget = 0x2303
ser = find_ALDO(vidTarget, pidTarget)
lib1785b.remoteMode(True, ser)

def occupiedPort():
    name = ser.name
    return name

def stepVolt(ser, v0, v1, t=5, dt=0.25):
    nt = t/dt
    dv = (v1-v0)/nt
    newV = v0
    for i in range(int(nt)):
        newV = newV + dv
        lib1785b.volt(newV, ser)
        time.sleep(dt)
    lib1785b.volt(newV, ser)
    lib1785b.volt(v1, ser)

def waitUntilVolt(volt, ser, timeout=10):
    counter = 0
    while not abs(float(lib1785b.readAll(ser)['vset']) - volt) <= 0.2:
        time.sleep(0.05)
        counter += 1
        if counter >= 20*timeout: # timeout seconds
            break
        
def getVoltage():
    return float(lib1785b.readAll(ser)['vset'])

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
        waitUntilVolt(0, ser)
        lib1785b.outputOn(False, ser)
    else:
        print("Setting ALDO voltage to " + str(voltage) + "V")
        lib1785b.outputOn(True, ser)
        stepVolt(ser, v0, v1, t, dt)

def onOff(on, t=5): #on == True for turning supply on, False for turning off
    v0 = float(lib1785b.readAll(ser)['vset'])
    isOn = ~lib1785b.readAll(ser)['output']
    if (on and isOn) or (not on and not isOn):
        #already in desired state
        time.sleep(0.01)
    elif (on and not isOn):
        print("Powering on ALDOs")
        lib1785b.volt(0, ser)
        lib1785b.outputOn(True, ser)
        stepVolt(ser, 0, v0, t, dt=0.25)
    elif (not on and isOn):
        print("Powering down ALDOs")
        stepVolt(ser, v0, 0, t, dt=0.25)
        lib1785b.outputOn(False, ser)
