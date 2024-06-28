def command(command, vi): vi.write(command)
def query(command, vi):
    vi.write(command)
    return vi.read_raw()

def setActiveChannel(channel, vi): command("inst:nsel " + str(channel), vi)

def remoteMode(state, vi): #turns remote mode on/off, depending on state
    # 0 for off, 1 for on
    cmd = "syst:rem" if state else "syst:loc"
    command(cmd, vi)

def seriesMode(state, vi): #turns series mode on/off (from 1/0)
    command("inst:com:trac NONE", vi)
    command("inst:com:para NONE", vi)
    cmd = "outp:ser " + str(state) #this one doesn't work
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

def queryVoltage(vi):
    cmd = "MEAS:VOLT?"
    query(cmd, vi)
    
