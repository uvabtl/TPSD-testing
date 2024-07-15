import time
import pyvisa as visa
import lib9130

rm=visa.ResourceManager()
li=rm.list_resources()
for index in range(len(li)):
    print(str(index)+" - "+li[index])
#choice = input("Which device?: ")
#vi=rm.open_resource(li[int(choice)])
vi=rm.open_resource(li[0])
print(vi.query("syst:addr?"))

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
        setVoltage(vi, newV)
        time.sleep(dt)
    setVoltage(vi, v1)

def volt(voltage, t=5):
    dt = 0.25
    v1 = float(voltage)
    v0 = float(lib9130.queryVoltage(vi))
    print("Setting Serenity voltage to " + str(v1))
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
    lib9130.remoteMode(1, vi) # enables remote mode

    #lib9130.seriesMode(0, vi) # should try to test series mode

    lib9130.setVoltage(10, vi)
    time.sleep(3)
    print(lib9130.queryVoltage(vi))
    stepVolt(vi, 10, 24) # set voltage to 24 from 10, over 5 seconds
    time.sleep(3)

    lib9130.setVoltageProt(50, vi) # attemps to set voltage protection to 50
    lib9130.setVoltage(48, vi) # attempts to set voltage to 48 (target)
    time.sleep(3)

    stepVolt(vi, 48, 30) # steps to 30V
    time.sleep(3)
    stepVolt(vi, 30, 0) # steps to 0V
    time.sleep(3)

    lib9130.remoteMode(0, vi) # disables remote mode
    lib9130.channelOff(1, vi) # disables channel 1

def tryQuery(vi):
    lib9130.remoteMode(1, vi)

    lib9130.channelOn(1, vi)
    
    #lib9130.setVoltage(10, vi)
    print(lib9130.queryChannel(vi))

#diagnostic(vi)
tryQuery(vi)
lib9130.seriesMode(0, vi)
