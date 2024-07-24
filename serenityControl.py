import time
import pyvisa as visa
import serial
import serial.tools.list_ports
import lib9130

def getSerenity(): # This has to be changed in order to set Serenity port manually.
    rm=visa.ResourceManager()
    li=rm.list_resources()
    #print(li)
    for dev in li:
        if "USB" in dev:
            try:
                #print(f"Trying {dev}")
                vi = rm.open_resource(dev)
                id = vi.query("*IDN?")
                print(id)
                vendor = id.split(",")[0]
                product = id.split(",")[1]
                if vendor=="BK" and product=="9130":
                    print(vi)
                    lib9130.remoteMode(vi)
                    return vi
            except:
                pass
    raise Exception("Couldn't find Serenity")

vi = getSerenity()
#vi = rm.open_resource("ASRL/dev/ttyUSB0::INSTR")

def occupiedPort():
    return vi.resource_info.resource_name

def setVoltage(vi, v1):
    if int(v1) > 30:
        lib9130.setVoltage(v1, vi)
    else:
        lib9130.setLowVoltage(v1, vi)
        
def stepVolt(vi, v0, v1, t=5, dt=0.25):
    v0 = float(lib9130.queryVoltage(vi))
    nt = t/dt
    dv = (v1-v0)/nt
    newV = v0
    for i in range(int(nt)):
        newV = newV + dv
        #print(f"Stepping to {newV}")
        setVoltage(vi, newV)
        time.sleep(dt)
    setVoltage(vi, v1)

def getVoltage():
    return float(lib9130.queryVoltage(vi))

def volt(voltage, t=5):
    dt = 0.25
    v1 = float(voltage)
    #print(f"querying voltage of {vi}")
    v0 = float(lib9130.queryVoltage(vi))
    print(f"Setting Serenity voltage to {v1} from {v0}")
    if v1 == 0:
        stepVolt(vi, v0, 0, t, dt)
        time.sleep((v0+0.01) / 6)
        lib9130.channelOff(1, vi)
    elif v1 == v0:
        lib9130.channelOn(1, vi)
    elif v1 > 48:
        print("Serenity voltage cannot exceed 48V.")
    else:
        lib9130.channelOn(1, vi)
        stepVolt(vi, v0, v1, t, dt)

def diagnostic(vi):
    lib9130.channelOn(1, vi) #enables channel 1
    lib9130.remoteMode(vi) # enables remote mode

    #lib9130.seriesMode(0, vi) # should try to test series mode

    lib9130.setVoltage(10, vi)
    time.sleep(3)
    print(lib9130.queryVoltage(vi))
    print("Setting voltage to 24")
    stepVolt(vi, 10, 24) # set voltage to 24 from 10, over 5 seconds
    time.sleep(3)
    print("Setting voltage to 50")
    lib9130.setVoltageProt(50, vi) # attemps to set voltage protection to 50
    lib9130.setVoltage(48, vi) # attempts to set voltage to 48 (target)
    time.sleep(3)
    print("Setting voltage to 30")
    stepVolt(vi, 48, 30) # steps to 30V
    time.sleep(3)
    print("Setting voltage to 0")
    stepVolt(vi, 30, 0) # steps to 0V
    time.sleep(3)

    lib9130.localMode(vi) # disables remote mode
    lib9130.channelOff(1, vi) # disables channel 1

    lib9130.remoteMode(vi)
    lib9130.channelOn(1, vi)

    volt(5)
    volt(10)
    volt(0)
    
def tryQuery(vi):
    lib9130.remoteMode(vi)

    lib9130.channelOn(1, vi)
    
    lib9130.setVoltage(10, vi)
    print(lib9130.queryChannel(vi))
    print(f"Voltage: {getVoltage(vi)}")

#global vi
#rm=visa.ResourceManager()
#vi = rm.open_resource("ASRL/dev/ttyUSB0::INSTR")
#vi = getSerenity()
#diagnostic(vi)
#tryQuery(vi)
#lib9130.seriesMode(0, vi)
#print(vi.resource_info.resource_name)
