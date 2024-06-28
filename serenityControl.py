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
#print(vi.query("*idn?"))

def setVoltage(vi, v1):
    if int(v1) > 30:
        lib9130.setVoltage(v1, vi)
    else:
        lib9130.setLowVoltage(v1, vi)
        
def stepVolt(vi, v0, v1, t=5, dt=0.25):
    nt = t/dt
    dv = (v1-v0)/nt
    newV = v0
    for i in range(int(nt)):
        newV = newV + dv
        setVoltage(vi, newV)
        time.sleep(dt)
    setVoltage(ser, v1)


#vi.write("outp:stat 1")
lib9130.channelOn(1, vi)
lib9130.remoteMode(1, vi)
#lib9130.seriesMode(0, vi)
lib9130.setVoltage(10, vi)
print(lib9130.queryVoltage(vi))
#lib9130.setVoltageProt(50, vi)
#lib9130.setVoltage(48, vi)
#lib9130.remoteMode(0, vi)
