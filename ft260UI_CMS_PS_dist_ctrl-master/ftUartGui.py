import PySimpleGUI as sg
import logging

from ft_function import *
from ft import findDeviceInPaths
from threading import Thread
import time
import signal


FT260_Vid = 0x0403
FT260_Pid = 0x6030

uartConfigDef = {
    'flowCtrl': FT260_UART_Mode.FT260_UART_XON_XOFF_MODE,
    'baudRate': 9600,
    'dataBit': FT260_Data_Bit.FT260_DATA_BIT_8,
    'stopBit': FT260_Stop_Bit.FT260_STOP_BITS_1,
    'parity': FT260_Parity.FT260_PARITY_NONE,
    'breaking': False
}
baudRateList = [1382400, 921600, 460800, 256000, 230400, 128000, 115200, 76800, 57600, 43000, 38400, 19200, 14400, 9600, 4800, 2400, 1200]

def openFtAsUart(Vid, Pid):
    ftStatus = c_int(0)
    handle = c_void_p()

    # mode 0 is I2C, mode 1 is UART
    ftStatus = ftOpenByVidPid(FT260_Vid, FT260_Pid, 1, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        logging.warning("Open device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        logging.info("Open device OK")

    ftStatus = ftUART_Init(handle)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        logging.error("Uart Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        logging.info("Uart Init OK")

    # config TX_ACTIVE for UART 485
    ftStatus = ftSelectGpioAFunction(handle, FT260_GPIOA_Pin.FT260_GPIOA_TX_ACTIVE)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        logging.warning("Uart TX_ACTIVE Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        logging.info("Uart TX_ACTIVE OK")

    return handle


def ftUartConfig(handle, cfgDit=uartConfigDef):
    # config UART
    ftUART_SetFlowControl(handle, cfgDit['flowCtrl']);
    ulBaudrate = c_ulong(cfgDit['baudRate'])
    ftUART_SetBaudRate(handle, ulBaudrate);
    ftUART_SetDataCharacteristics(handle, cfgDit['dataBit'], cfgDit['stopBit'], cfgDit['parity']);
    if cfgDit['breaking']:
        ftUART_SetBreakOn(handle)
    else:
        ftUART_SetBreakOff(handle)

    uartConfig = UartConfig()
    ftStatus = ftUART_GetConfig(handle, byref(uartConfig))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        logging.warning("UART Get config NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        logging.info("config baud:%ld, ctrl:%d, data_bit:%d, stop_bit:%d, parity:%d, breaking:%d\r\n" % (
            uartConfig.baud_rate, uartConfig.flow_ctrl, uartConfig.data_bit, uartConfig.stop_bit, uartConfig.parity, uartConfig.breaking))



def ftUartWrite(handle, data=b''):
    # Write data
    dwRealAccessData = c_ulong(0)
    bufferData = c_char_p(data)
    buffer = cast(bufferData, c_void_p)
    ftStatus = ftUART_Write(handle, buffer, len(data), len(data), byref(dwRealAccessData))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        logging.warning("UART Write NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        logging.info("Write bytes : %d\r\n" % dwRealAccessData.value)



class ftUartReadLoop:

    def __init__(self, handle):
        self._handle = handle
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        dwRealAccessData = c_ulong(0)
        dwAvailableData = c_ulong(0)
        buffer2Data = c_char_p(b'\0'*200)
        buffer2 = cast(buffer2Data, c_void_p)
        while self._running:
            # Read data
            memset(buffer2Data, 0, 200)
            ftUART_GetQueueStatus(self._handle, byref(dwAvailableData))
            if dwAvailableData.value == 0:
                continue
            logging.info("dwAvailableData : %d\r\n" % dwAvailableData.value)

            ftStatus = ftUART_Read(self._handle, buffer2, 50, dwAvailableData, byref(dwRealAccessData))
            if not ftStatus == FT260_STATUS.FT260_OK.value:
                logging.info("UART Read NG : %s\r\n" % FT260_STATUS(ftStatus))
            else:
                buffer2Data = cast(buffer2, c_char_p)
                logging.info("Read bytes : %d\r\n" % dwRealAccessData.value)
                if dwAvailableData.value > 0:
                    print("%s" % buffer2Data.value.decode('ascii'), end='')

        time.sleep(0.1)


is_sigInt_up = False

def sigint_handler(sig, frame):
    logging.info("SIGINT")
    global is_sigInt_up
    is_sigInt_up = True


def main():
    logging.basicConfig(filename='ftUart.log', level=logging.INFO)
    if not findDeviceInPaths(FT260_Vid, FT260_Pid):
        sg.Popup("No FT260 Device")
        exit()

    uartHandle = openFtAsUart(FT260_Vid, FT260_Pid)
    if not uartHandle:
        sg.Popup("open uartHandle error")
        exit()

    ftUartConfig(uartHandle)
    ftUartR = ftUartReadLoop(uartHandle)
    tr = Thread(target=ftUartR.run)
    signal.signal(signal.SIGINT, sigint_handler)
    tr.start()

    cfgFrame_lay = [
                [sg.Text('Flow Ctrl', size=(10, 1)), sg.InputCombo([i.name for i in FT260_UART_Mode], default_value = uartConfigDef['flowCtrl'].name, size=(30,1), key="flowCtrl", change_submits=True)],
                [sg.Text('Baud Rate', size=(10, 1)), sg.InputCombo(baudRateList, default_value = uartConfigDef['baudRate'], size=(30,1), key="baudRate", change_submits=True)],
                [sg.Text('Data Bits', size=(10, 1)), sg.InputCombo([i.name for i in FT260_Data_Bit], default_value = uartConfigDef['dataBit'].name, size=(30,1), key="dataBit", change_submits=True)],
                [sg.Text('Parity', size=(10, 1)), sg.InputCombo([i.name for i in FT260_Parity], default_value = uartConfigDef['parity'].name, size=(30,1), key="parity", change_submits=True)],
                [sg.Text('Stop Bits', size=(10, 1)), sg.InputCombo([i.name for i in FT260_Stop_Bit], default_value = uartConfigDef['stopBit'].name, size=(30,1), key="stopBit", change_submits=True)],
                [sg.Text('Breaking', size=(10, 1)), sg.Checkbox('', default = uartConfigDef['breaking'], size=(30,1), key="breaking", change_submits=True)],
                    ]
    upFrame = [[sg.Output(size=(80, 30)), sg.Frame("Config", cfgFrame_lay, size=(50, 30))]]

    send_lay = [[sg.Multiline(focus=True, size=(100, 5), enter_submits=False, key="send", do_not_clear=True), sg.ReadButton('Send', bind_return_key=True)]]
    help_lay = [[sg.Text('Help')]]
    downFrame = [[sg.TabGroup([[sg.Tab('Send', send_lay), sg.Tab('Help', help_lay)]])]]

    layout = [
        [sg.Frame('', upFrame, size=(130, 30))],
        [sg.Frame('', downFrame, size=(130, 5))]
            ]


    window = sg.Window('FT260 UART').Layout(layout)

    # ---===--- Loop taking in user input and using it to call scripts --- #
    while True:
        (button, value) = window.Read()
        #sg.Popup('The button clicked was "{}"'.format(button), 'The values are', value)
        global is_sigInt_up
        if is_sigInt_up or button is None: # window.Read will block
            logging.info("Close Uart Handle")
            ftUartR.stop()
            ftClose(uartHandle)
            #time.sleep(1)
            tr.join()
            break # exit button clicked
        elif button == 'Send':
            ftUartWrite(uartHandle, bytes(value["send"][:-1], 'ascii'))
        elif button in [ i for i in uartConfigDef]:
            uartCfg = {
            'flowCtrl': FT260_UART_Mode[value['flowCtrl']],
            'baudRate': int(value['baudRate']),
            'dataBit': FT260_Data_Bit[value['dataBit']],
            'stopBit': FT260_Stop_Bit[value['stopBit']],
            'parity': FT260_Parity[value['parity']],
            'breaking': value['breaking']
            }
            ftUartConfig(uartHandle, cfgDit=uartCfg)



main()
