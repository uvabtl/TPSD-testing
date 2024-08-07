# TPSD-testing
Repo to remotely control the power supplies and TPSD board from a GUI. Most of the GUI code was adapted from Paolo's repo, but new elements have been added for directly altering the input voltages. This also includes a ramp for changing the voltage over a set period of time. 

To run the GUI without connecting to a board, disable the import statements for aldoControl, tecControl, and bpolControl in the ftI2gui file. The only major changes that have to be implemented to control all power sources at once are changing the ports named in the above files and enabling the second bPOL12 power supply in its control file, then uncommenting the import statements in the main ftI2gui file. The program is run from ftI2gui.py. Note that using the aldo/tec/bpol controls requires root access currently.

In addition, new GUI elements are also added to control the power supply correponding to the Serenity. This supply is currently a BK 9130, but this might be changed in the future so as to allow for remote control of the power supply's series mode. A new window was added to control the Serenity, as it didn't make sense to add Serenity control directly to the TPSD elements, since the Serenity only connects to one of the readout units. Also added was a live plot of all the power supplies' voltages.

The original README from Paolo's repo is below, with an additional section on setting up the power supply controls:
***
# I2C Python3.6+ GUI for [FT260](https://www.ftdichip.com/Products/ICs/FT260.html) chip & CMS BTL power supply distribution board control

This GUI provides manual control over FT260 chip acting as USB to I2C master converter.
The FT260 is mounted on the CMS BTL power supply distribution control and is interfaced with two PCA9555 GPIO expanders.

The board is used to selectively power on/off the supplies of each (out of 6) Readout Unit (RU).

The power supplies are 3 (current consumption per RU):
* bPOL12V supply: <12 V, 4 A 
* TEC supply: max 32 V, 1 A
* ALDO supply: max 48 V, 0.1 A
The Serenity power supply is (attached to only 1 RU at a time):
* Serenity supply: max 48 V, 3 A
## Functionality (generic I2C use)

I2C address scanner. It shows 7 bit addresses that acknowledge themselves on the bus.

Register read/write. Many devices have internal configuration registers. Register access is done by writing register 
address first, then either writing its new value, or initiating new read sequence to retrieve current value.
Register address size 8/16 bit and register word size 8/16/32 bit can be selected.     

I2C bus log. Every bus data transfer is given a sequential number, a timestamp, read/write feature,
slave device address, data content, start/stop flags and bus status.
Message byte order corresponds to the order of byte transfer on the bus.
Bus status flag is not decoded. You can reference it with FT260 documentation.

An standalone executable can be easily build with PyInstaller.

## Functionality (CMS BTL PS distribution board control)

The `Init board` button initializes the settings of the PCA9555s and sets the default of each channel to `off`.

The individual (`RU#`) `ON` or `OFF` buttons configure the corresponding switch.

The general `ALL PS&RU` and `ALL PS&RU` buttons configure all switches on the board, or all switches on a specific
power supply.

The voltage blank fields in each column allow for a voltage to be entered for each power supply, which is then applied to the system with the 'SET' buttons. This is changed over time, according to the setting of the 'ramp' dropdown. All three power supplies for the TPSD board share the same ramp setting, and the Serenity control has its own ramp dropdown.

### IMPORTANT

The ALDO switches cannot be toggled (by hardware) if the input power supply is above 3 V.
If the user tries to do that, a warning appears and the setting is not applied.

## Requirements

Windows (fully tested) or Linux (beta support). Python 64-bit is required on Windows.
The GUI is built with tkinter library.

Using Linux can cause the USB connection to the ft260 chip to fail. In the most recent case, this was due to an update to the kernel.

## Run Gui

* `pip install tkinter`
* `pip install smbus2` (Linux only)
* `python ftI2cGui.py`

## Run Power Supply Controls

* `pip install pyserial`
* Find the USB ports connected to supplies, then change port names in the aldo/tec/bpol Control files
  
## Build standalone application

* `pip install PyInstaller`
* `pyinstaller -wF ftI2cGui.py` to Build **dist\ftI2cGui.exe**
* `mkdir dist\lib && copy lib\LibFT260.dll dist\lib\`
* then you can run **ftI2cGui.exe** in dist directory

## Attached Devices
The power supplies are attached via USB. Once several are connected at once, it will be important to detect which is which automatically. Each one is listed here with VID and PID for identification.

ALDO Power: BK 1787B Power Supply
  * VID: 0x067b
  * PID: 0x2303
  * Display Name: Prolific Technology, Inc. PL2303 Serial Port / Mobile Action MA-8910P

TEC Power: BK 1687B Power Supply
  * VID: 0x10c4
  * PID: 0xea60
  * Display Name: Silicon Labs CP210x UART Bridge

bPOL Power: BK 1688b Power Supply
  * VID: 0x10c4
  * PID: 0xea60
  * Display Name: Silicon Labs CP210x UART Bridge

Serenity Power: BK 9130 Power Supply
  * VID: 0x067b
  * PID: 0x2303
  * Display Name: Prolific Technology, Inc. PL2303 Serial Port / Mobile Action MA-8910P

These were read off of the output of `lsusb` in the terminal; it seems likely that they are the USB cords connecting the computer to the devices. This is why the ALDOs appear to match the Serenity power supply; they have the same USB adapter connected to them.
