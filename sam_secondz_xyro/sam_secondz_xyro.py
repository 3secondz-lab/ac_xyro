import time
import math
import sys
import os
import platform

if platform.architecture()[0] == "64bit":
    sysdir = "stdlib64"
else:
    sysdir = "stdlib"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), sysdir))
os.environ['PATH'] = os.environ['PATH'] + ";."

import ac
import acsys

import xyrodevice


appWindow=0
lastTimeUpdate=0
running = True

hSession = None

showWindowTitle = True
appWindowActivated = 0


#debug output label, ignore this
dbgLabel = 0



#Ini overwritable constants
UDP_IP = "127.0.0.1"
UDP_PORT = 59481
# End of ini
MESSAGE = "Hello, World!"

#sock = None;
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

xyro_dev = None
DebugInput = None

BtnStart = None
BtnStop = None

def acMain(ac_version):
    global appWindow, dbgLabel
    global xyro_dev
    global DebugInput
    global BtnStart, BtnStop

    try:
        import sam_secondz_xyro_config
        sam_secondz_xyro_config.handleIni('3secondz_xyro')
        
        ac.log("3secondz_xyro:: xyro created")
        xyro_dev = xyrodevice.XyroDevice(UDP_IP, UDP_PORT)

        appWindow=ac.newApp("3secondz_xyro")
        ac.setSize(appWindow,300,100)
        ac.drawBorder(appWindow,0)
        ac.setBackgroundOpacity(appWindow,0)
        ac.setTitle(appWindow, '3secondz_xyro')
        
        IPAddrInput = ac.addTextInput(appWindow,"TEXT_INPUT")
        ac.setPosition(IPAddrInput,10,30)
        ac.setSize(IPAddrInput,120,20)
        ac.setText(IPAddrInput, str(UDP_IP))
        
        PortInput = ac.addTextInput(appWindow,"TEXT_INPUT")
        ac.setPosition(PortInput,140,30)
        ac.setSize(PortInput,50,20)
        ac.setText(PortInput, str(UDP_PORT))
        
        DebugInput = ac.addTextInput(appWindow,"TEXT_INPUT")
        ac.setPosition(DebugInput,10,60)
        ac.setSize(DebugInput,280,20)
        ac.setText(DebugInput, "")
        
        BtnStart = ac.addButton(appWindow, "Start")
        ac.setPosition(BtnStart, 10, 90)
        ac.setSize(BtnStart,90,20)
        ac.addOnClickedListener(BtnStart, onClickBtnStart)
        
        BtnStop = ac.addButton(appWindow, "Stop")
        ac.setPosition(BtnStop, 110, 90)
        ac.setSize(BtnStop,90,20)
        ac.addOnClickedListener(BtnStop, onClickBtnStop)
        

        ac.addRenderCallback(appWindow , onFormRender)
        ac.addOnAppActivatedListener(appWindow,onAppActivated)
        appWindowActivated = time.clock()
        showWindowTitle = True

        dbgLabel = ac.addLabel(appWindow, "")
        ac.setPosition(dbgLabel, 15, 405)
        
        xyro_dev.start()
        
        ac.log("3secondz_xyro::acMain finished")
    except Exception as e:
        ac.log("3secondz_xyro::acMain() %s" % e)
    return "3secondz_xyro"



def onAppActivated(*args):
    global appWindowActivated, showWindowTitle
    
    ac.log("3secondz_xyro::onAppActivated({0})".format(args))
    appWindowActivated = time.clock()
    showWindowTitle = True
    ac.setBackgroundOpacity(appWindow, 0.5)
    ac.setIconPosition(appWindow, 0, 0)
    ac.setTitle(appWindow, '3secondz_xyro')
    running = True



def acShutdown():
    global xyro_dev
    xyro_dev.stop()
    running = False
    hSession = None
    centerOffset = None
    ac.removeItem(appWindow)




def onFormRender(deltaT):
    global showWindowTitle, appWindowActivated, appWindow, dbgLabel
    global xyro_dev
    global DebugInput
    if running == False:
        return

    #Important: Other apps can alter the global ac.gl Color and Alpha; let's reset this to White
    # ac.glColor4f(1,1,1,1)

    #Show/Hide the title shortly after the app became visible
    # if showWindowTitle:
        # if (time.clock() - appWindowActivated > showTitle):
            # showWindowTitle = False
            # ac.setBackgroundOpacity(appWindow, 0)
            # ac.setIconPosition(appWindow, -7000, -3000)
            # ac.setTitle(appWindow, "")


    #Important: We'll clean the color again, so we might not affect other apps
    # ac.glColor4f(1,1,1,1)
    
    #if sock != None:
    try:
        # MESSAGE = "speed: " + str(int(info.physics.speedKmh))
        #MESSAGE = "speed: " + str(int(ac.getCarState(0, acsys.CS.SpeedKMH)))
        # sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
        if xyro_dev == None:
            ac.log("3secondz_xyro::xyro none")
        else:
            if xyro_dev.isOn():
                #xyro_dev.sendInfo()
                command = xyro_dev.recvInfo()
                ac.setText(DebugInput, command.decode())
                # ac.log("3secondz_xyro::onFormRender() Something sent")
            # else:
                # ac.log("3secondz_xyro::onFormRender() xyro off")
            
    except Exception as e:
        ac.log("3secondz_xyro::onFormRender() %s" % e)
    
    

def onClickBtnStart(*args):
    ac.console("Started")
    xyro_dev.sendAlivePacketStart()
    
def onClickBtnStop(*args):
    ac.console("Stopped")
    xyro_dev.sendAlivePacketStop()