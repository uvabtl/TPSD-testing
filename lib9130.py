''' 
Major issues:
Series mode does not work. I am not sure if this command is included in the 9130 model; it seems to be exclusive to the 9130B and 9130C.
I can neither enable nor disable series mode remotely.

When in series mode, I don't know how to make the instrument recognize it and increase the voltage limits. I can change the combined voltage of the channel,
but this is still capped at 30V.

I can edit the voltage protection in the supply, but I am not able to increase this cap beyond 31V either.
'''

def command(command, vi): vi.write(command)
def query(command, vi): return vi.query(command) #returns output of the query

def localMode(vi): command("SYST:LOC", vi)
def remoteMode(vi): command("SYST:REM", vi)

def setActiveChannel(channel, vi): command("inst:nsel " + str(channel), vi)

def seriesMode(state, vi): #turns series mode on/off (from 1/0)
    command("inst:com:trac NONE", vi)
    command("inst:com:para NONE", vi)
    cmd = "outp:ser" if state else "inst:com:ser NONE" #this one doesn't work
    command(cmd, vi)
    
def channelOn(channel, vi): # input is "1", "2", or "3"
    setActiveChannel(channel, vi)
    command("outp on", vi)
    
def channelOff(channel, vi): #input is "1", "2", or "3"
    setActiveChannel(channel, vi)
    command("outp off", vi)

def setLowVoltage(volt, vi): # for voltages requiring only channel 1
    cmd = "volt " + str(volt) + "V"
    command(cmd, vi)

def setVoltage(volt, vi):
    cmd = "volt " + str(volt) + "V"
    command(cmd, vi)

def setVoltageProt(volt, vi):
    cmd = "volt:prot " + str(volt) + "V, volt prot MAX"
    command(cmd, vi)

def queryOnOff(channel, vi):
    setActiveChannel(channel, vi)
    cmd = "OUTP?"
    return query(cmd, vi)

def queryVoltage(vi):
    cmd = "meas:volt?"
    return query(cmd, vi)

def queryProt(vi):
    cmd = "volt:prot?"
    return query(cmd, vi)
    
def queryChannel(vi):
    cmd = "inst:nsel?"
    return query(cmd, vi)