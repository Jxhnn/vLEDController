from pyfirmata import Arduino, util, pyfirmata
from array import array
import threading
import time
import bimpy

finalCom = 1 # Minimum port is 1
maxInterval = bimpy.Float()
pinNumber = bimpy.Int()
minPWM = bimpy.Int(0)
maxPWM = bimpy.Int(1)
# trueBool = bimpy.Bool(True)
toggleLight = False
plot_values = array('f',[])
textToggleButton = 'Start flashing LED'
buttonNewColorEnabled = bimpy.Vec4(0,0.33,0.0078,1);

# bimpy.push_style_color(bimpy.Colors.Button,buttonColoredEnabled)

def checkPWM():
    if (currentBoard.digital[pinNumber.value].mode == pyfirmata.PWM):
        return 1
    try:
        currentBoard.digital[pinNumber.value].mode = pyfirmata.PWM
        return 1
    except:
        return 0

def flashLED():
    for i in range(0,9999999):
        if (toggleLight == True):
            currentInterval = maxInterval.value
            pin = pinNumber.value
            if (checkPWM() == 1):
                currentBoard.digital[pin].write(round(maxPWM.value/255,2))
            else:
                currentBoard.digital[pin].write(1)
            plot_values.append(1)
            if (len(plot_values) > 40):
                plot_values.pop(0)
            time.sleep(float(currentInterval))
            # print(currentBoard.digital[pin].read())
            if (checkPWM() == 1):
                currentBoard.digital[pin].write(round(minPWM.value/255,2))
            else:
                currentBoard.digital[pin].write(0)
            plot_values.append(0)
            if (len(plot_values) > 40):
                plot_values.pop(0)
            time.sleep(float(currentInterval))
        else:
            return

print('Checking communication..')

for nx in range(0,30):
    try:
        testBoard = Arduino('COM' + str(nx))
        testBoard.exit()
        finalCom = nx
    except:
        continue

print('Found Arduino port : COM' + str(finalCom))
try:
    currentBoard = Arduino('COM' + str(finalCom))
except:
    print('Error while connecting to the serial port.')
    currentBoard.exit()
    time.sleep(3)
try:
    acquisition = util.Iterator(currentBoard)
    acquisition.start()
except:
    print('acquisition problem ! Please try again.')
    currentBoard.exit()
    time.sleep(3)

ctx = bimpy.Context()
ctx.init(470, 300, "")
while(not ctx.should_close()):
    ctx.new_frame()
    if bimpy.begin("Arduino Controller", flags=(bimpy.WindowFlags.NoSavedSettings | bimpy.WindowFlags.NoMove | bimpy.WindowFlags.NoResize | bimpy.WindowFlags.AlwaysAutoResize | bimpy.WindowFlags.NoCollapse)):
        bimpy.push_style_var(bimpy.Style.WindowRounding, 0)
        bimpy.push_style_var(bimpy.Style.FrameRounding, 12)
        bimpy.push_style_var(bimpy.Style.Alpha, 255)
        bimpy.input_int("LED Pin (digital)",pinNumber,1)
        if (pinNumber.value < 2):
            pinNumber = bimpy.Int(2)
        if (pinNumber.value > 13):
            pinNumber = bimpy.Int(13)
        if (minPWM.value > 255):
            minPWM = bimpy.Int(255)
        if (minPWM.value < 0):
            minPWM = bimpy.Int(0)
        if (maxPWM.value > 255):
            maxPWM = bimpy.Int(255)
        if (maxPWM.value < 1):
            maxPWM = bimpy.Int(1)
        if (minPWM.value > maxPWM.value):
            minPWM = bimpy.Int(maxPWM.value)
        bimpy.input_float('Light interval (seconds)', maxInterval, 0.100000000000000)
        if (maxInterval.value < 0.100000000):
            maxInterval = bimpy.Float(0.100000000000000)
        if bimpy.button(textToggleButton,bimpy.Vec2(208,0)):
                toggleLight = not toggleLight
                if (toggleLight == True):
                    plot_values = array('f',[])
                    textToggleButton = 'Stop flashing LED'
                    threading.Thread(target=flashLED, args=()).start()
                if (toggleLight == False):
                    textToggleButton = 'Start flashing LED'
        if (checkPWM() == 1):
            bimpy.input_int('PWM Min',minPWM,1)
            bimpy.input_int('PWM Max',maxPWM,1)
        bimpy.plot_lines("",plot_values,0,'(' + str(pinNumber.value) + ')',0,1,bimpy.Vec2(0,50))
        if bimpy.button('Exit',bimpy.Vec2(208,0)):
            currentBoard.exit()
            exit()
    bimpy.end()
    ctx.render()
