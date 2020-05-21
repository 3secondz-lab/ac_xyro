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
from sim_info import info


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
DEVICE_ID = 0xac00000000000001
FW_VERSION = "100B".encode().ljust(10,b'\0')
STEERING_ANGLE_RANGE = 1080
ALIVE_PACKET_PERIOD = 1.0
CAN_PACKET_PERIOD = 0.05
MEAS_PACKET_PERIOD = 0.05
NAV_PACKET_PERIOD = 0.1

# dev server
#UDP_IP = "15.165.61.176"
#UDP_PORT = 11327

# live server
#UDP_IP = "15.165.61.176"
#UDP_PORT = 11325

# End of ini
MESSAGE = "Hello, World!"

#sock = None;
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

xyro_dev = None
DebugInput = None
DebugInput2 = None
DebugInput3 = None

BtnStart = None
BtnStop = None

def acMain(ac_version):
    global appWindow, dbgLabel
    global xyro_dev
    global DebugInput, DebugInput2, DebugInput3
    global BtnStart, BtnStop

    try:
        import sam_secondz_xyro_config
        sam_secondz_xyro_config.handleIni('3secondz_xyro')
        
        ac.log("3secondz_xyro:: xyro created")
        xyro_dev = xyrodevice.XyroDevice(UDP_IP, UDP_PORT, DEVICE_ID, FW_VERSION, STEERING_ANGLE_RANGE, ALIVE_PACKET_PERIOD, CAN_PACKET_PERIOD, NAV_PACKET_PERIOD, MEAS_PACKET_PERIOD)

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
        
        DebugInput2 = ac.addTextInput(appWindow,"TEXT_INPUT")
        ac.setPosition(DebugInput2,10,90)
        ac.setSize(DebugInput2,280,20)
        ac.setText(DebugInput2, "")
        
        DebugInput3 = ac.addTextInput(appWindow,"TEXT_INPUT")
        ac.setPosition(DebugInput3,10,120)
        ac.setSize(DebugInput3, 280,20)
        ac.setText(DebugInput3, "")
        
        BtnStart = ac.addButton(appWindow, "Start")
        ac.setPosition(BtnStart, 10, 150)
        ac.setSize(BtnStart,90,20)
        ac.addOnClickedListener(BtnStart, onClickBtnStart)
        
        BtnStop = ac.addButton(appWindow, "Stop")
        ac.setPosition(BtnStop, 110, 150)
        ac.setSize(BtnStop,90,20)
        ac.addOnClickedListener(BtnStop, onClickBtnStop)
        

        ac.addRenderCallback(appWindow , onFormRender)
        ac.addOnAppActivatedListener(appWindow,onAppActivated)
        appWindowActivated = time.clock()
        showWindowTitle = True

        dbgLabel = ac.addLabel(appWindow, "")
        ac.setPosition(dbgLabel, 15, 405)
        
        #xyro_dev.turnOn()
        
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
    xyro_dev.turnOff()
    running = False
    hSession = None
    centerOffset = None
    ac.removeItem(appWindow)




def onFormRender(deltaT):
    global showWindowTitle, appWindowActivated, appWindow, dbgLabel
    global xyro_dev
    global DebugInput, DebugInput2, DebugInput3
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
            
                ### FOR DEBUG ONLY
                ## AC-GPS conversion
                # car_pos = list(ac.getCarState(0, acsys.CS.WorldPosition))
                # car_pos_tmp = [0, 0, 0]
                # car_pos_tmp[0] = round(car_pos[0], 1)
                # car_pos_tmp[1] = round(-car_pos[2], 1)
                # car_pos_tmp[2] = round(car_pos[1], 1)
                # ac.setText(DebugInput, "AC: " + str(car_pos_tmp))
                
                # tmp_result = xyro_dev.getCarPosition()
                # ac.setText(DebugInput2, "GPS: " + str(tmp_result))
                
                
                ### FOR DEBUG ONLY
                ## UDP packet send interval
                # tmp_result = int(xyro_dev.timerSendCanActualInterval * 1000)
                # ac.setText(DebugInput, "Packet Interval: " + str(tmp_result).rjust(4, ' ') + "ms")
                # ac.setText(DebugInput2, "Dev ID: " + hex(DEVICE_ID))
                
                ### FOR DEBUG ONLY
                ## AccG
                # tmp_result = int((info.physics.accG[2] * 9.81 * (2**10)))
                # ac.setText(DebugInput, "AccG_X: " + str(tmp_result).rjust(8, ' ') + "")
                # tmp_result = int((info.physics.accG[0] * 9.81 * (2**10)))
                # ac.setText(DebugInput2, "AccG_Y: " + str(tmp_result).rjust(8, ' ') + "")
                # tmp_result = int((info.physics.accG[1] * 9.81 * (2**10)))
                # ac.setText(DebugInput3, "AccG_Z: " + str(tmp_result).rjust(8, ' ') + "")
                
                ### FOR DEBUG ONLY
                ## LocalAngularVelocity
                tmp_result = int(info.physics.localAngularVel[2] * 180 / math.pi * (2**12))
                ac.setText(DebugInput, "AngVel_X: " + str(tmp_result).rjust(12, ' ') + "")
                tmp_result = int(info.physics.localAngularVel[0] * 180 / math.pi * (2**12))
                ac.setText(DebugInput2, "AngVel_Y: " + str(tmp_result).rjust(12, ' ') + "")
                tmp_result = int(info.physics.localAngularVel[1] * 180 / math.pi * (2**12))
                ac.setText(DebugInput3, "AngVel_Z: " + str(tmp_result).rjust(12, ' ') + "")
                
                ### FOR DEBUG ONLY
                ## heading
                # tmp_var = int(((info.physics.heading + math.pi) * 180 / math.pi) * (10**5))
                # ac.setText(DebugInput2, "AC: " + str(tmp_var))
                
                ### FOR DEBUG ONLY
                ## heading
                # ac.setText(DebugInput, "turboBoost: " + str(info.physics.turboBoost))
                # ac.setText(DebugInput2, "Dev Tick: " + str(xyro_dev.printDebugMsg()[1]))
                
                
                ## PROCESS COMMAND RECEIVED FROM SERVER
                #xyro_dev.sendInfo()
                command = xyro_dev.recvInfo()
                #ac.setText(DebugInput, command.decode())
                
                ac.console(str(command))
                
                
                
                
                # ac.log("3secondz_xyro::onFormRender() Something sent")
            # else:
                # ac.log("3secondz_xyro::onFormRender() xyro off")
            
    except Exception as e:
        ac.log("3secondz_xyro::onFormRender() %s" % e)
    
    

def onClickBtnStart(*args):
    xyro_dev.start()
    
def onClickBtnStop(*args):
    ac.console("Stopped")
    xyro_dev.stop()

