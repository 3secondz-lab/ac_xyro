import euclid
import ac
import acsys
import math

import socket
from sim_info import info
from struct import *
from threading import Timer
import time





PACKET_CAN = 0x10000 # 뒷 4자리는 CAN ID
PACKET_ALIVE = 0x00001  # alive packet
PACKET_NAV_PVT = 0x00002  # ublox NAV_PVT packet
PACKET_START = 0x00003
packettype = 0x00001

CLASS_ID_ALIVE = 0x00
CLASS_ID_START = 0x01
CLASS_ID_CAN = 0x04
CLASS_ID_OBD_FAST = 0x05
CLASS_ID_OBD_SLOW = 0x06
CLASS_ID_OBD_DATA = 0x07
CLASS_ID_SERVER_WIFI = 0x11
CLASS_ID_STOP = 0x12
CLASS_ID_OBD_PID = 0x13
CLASS_ID_FW_UPDATE = 0x14
CLASS_ID_FW_VERSION = 0x15
CLASS_ID_RESET = 0x16

DEV_STATUS_DEAD = 0x00 # off
DEV_STATUS_BREATHING = 0x01 # sending 
DEV_STATUS_STARTED = 0x02





class XyroDevice(object):
    name = "player name"
    #deviceOn = False
    deviceStatus = DEV_STATUS_DEAD
    destIP = "127.0.0.1"
    destPort = 59481
    localIP = "127.0.0.1"
    localPort = 59482
    message = ""
    sock = None
    time_device_start = 0
    
    deviceId = 0
    
    sendAlivePacketRunning = False
    timerSendAlive = None
    timerSendAliveInterval = 2.0
    
    sendDataPacketRunning = False
    timerSendData = None
    timerSendDataInterval = 0.05
    timerSendDataActualInterval = 0
    timerSendDataTimePrev = time.time()
    
    [x0, y0] = [0, 0]
    [x0p, y0p] = [0, 0]
    scale_factor = 1
    theta_rad = 0

    def __init__(self, serverIP, serverPort, deviceId):
        ac.log("XyroDevice::__init__()")
        #self.deviceOn = False
        self.deviceStatus = DEV_STATUS_DEAD
        self.destIP = serverIP
        self.destPort = serverPort
        self.deviceId = deviceId
        self.time_device_start = time.time()
        #ac.console("Device ID: " + str(self.deviceId))
        #ac.console("start time : " + str(self.time_device_start))
        
        self.coordinateCoverterInit()
        self.turnOn()
        

    def turnOn(self):
        ac.log("XyroDevice::setup()")
        try:
            if self.deviceStatus == DEV_STATUS_DEAD:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
                self.sock.connect((self.destIP, self.destPort))
                #self.sock.bind((self.localIP, self.localPort))
                self.sock.setblocking(0)
                self.deviceStatus = DEV_STATUS_BREATHING
                self.sendAlivePacketStart()
                ac.console("Start to breathe..")
        except Exception as e:
            ac.log("XyroDevice::setup() %s" % e) 
            
            
    def turnOff(self):
        if self.deviceStatus == DEV_STATUS_STARTED:
            self.stop()
        self.sendAlivePacketStop()
        self.deviceStatus = DEV_STATUS_DEAD
        self.sock.close()

    def start(self):
        if self.deviceStatus == DEV_STATUS_BREATHING:
            ac.log("XyroDevice::start()")
            ac.console("XyroDevice::start()")
            self.deviceStatus = DEV_STATUS_STARTED
            self.sendDataPacketStart()

    def stop(self):
        if self.deviceStatus == DEV_STATUS_STARTED:
            ac.log("XyroDevice::stop()")
            ac.console("XyroDevice::stop()")
            self.sendDataPacketStop()
            self.deviceStatus = DEV_STATUS_BREATHING

    def recvInfo(self):
        recv_message = self.sock.recvfrom(1024)
        #self.sock.send(self.generatePacket(PACKET_START))
        
        ######### process received command
        
        
        return recv_message[0]
    
    def isOn(self):
        if self.deviceStatus == DEV_STATUS_STARTED:
            return True
        elif self.deviceStatus == DEV_STATUS_BREATHING:
            return True
        else:
            return False
        
        
    #############################
    #  ALIVE PACKET START/STOP
    #############################
    def sendAlivePacketRun(self):
        self.sendAlivePacketRunning = False
        self.sendAlivePacketStart()
        
        # actual task
        try:
            if self.isOn() == True:
                #self.sock.sendto(self.generatePacket(PACKET_ALIVE), (self.destIP, self.destPort))
                self.sock.send(self.generatePacket(PACKET_ALIVE))
        except Exception as e:
            ac.log("XyroDevice %s" % e)
            ac.console(e)
        # ac.console("XyroDevice::sendAlivePacketRun()")
        
    def sendAlivePacketStart(self):
        if not self.sendAlivePacketRunning:
            self.timerSendAlive = Timer(self.timerSendAliveInterval, self.sendAlivePacketRun)
            self.timerSendAlive.start()
            self.sendAlivePacketRunning = True
            
    def sendAlivePacketStop(self):
        self.timerSendAlive.cancel()
        self.sendAlivePacketRunning = False
        
        
    #############################
    #  DATA PACKET START/STOP
    #############################
    def sendDataPacketRun(self):
        self.sendDataPacketRunning = False
        self.sendDataPacketStart()
        
        # actual task
        try:
            if self.deviceStatus == DEV_STATUS_STARTED:
                current_time = time.time()
                self.timerSendDataActualInterval = current_time - self.timerSendDataTimePrev
                self.timerSendDataTimePrev = current_time
                # NAV_PVT packet
                #self.sock.sendto(self.generatePacket(PACKET_NAV_PVT), (self.destIP, self.destPort))
                self.sock.send(self.generatePacket(PACKET_NAV_PVT))
                pass
                # CAN data
                
                # ESF_MEAS packet
                
        except Exception as e:
            ac.log("XyroDevice %s" % e)
            ac.console(e)
        # ac.console("XyroDevice::sendAlivePacketRun()")
        
    def sendDataPacketStart(self):
        if not self.sendDataPacketRunning:
            self.timerSendData = Timer(self.timerSendDataInterval, self.sendDataPacketRun)
            self.timerSendData.start()
            self.sendDataPacketRunning = True
        
    def sendDataPacketStop(self):
        self.timerSendData.cancel()
        self.sendDataPacketRunning = False
        
    #############################
    #  PACKET GENERATION
    #############################
    def generatePacket(self, packetType):
        packed_packet = b'\x00'
        try:
            packet_header = 0x62B5
            packet_class = 0x39
            packet_id = 0x10
            packet_deviceId = self.deviceId
            
            #packet_device_tick = 0
            #packet_payload = b'\x00'
            #packet_length = 0
            #packet_checksum = b'\x00'
            
            packet_deviceTick = self.getDeviceTick()
            packet_payload = self.generateInnerPacket(packetType)
            packet_length = 8+4+len(packet_payload)
            packet_checksum = self.calcUbxChecksum(packet_class, packet_id, pack('H', packet_length) + pack('>Q', packet_deviceId) +  pack('I', packet_deviceTick) + packet_payload)
            
            packed_packet = pack('HBBH', packet_header, packet_class, packet_id, packet_length) + pack('>Q', packet_deviceId) +  pack('I', packet_deviceTick) + packet_payload + packet_checksum
            
            
        except Exception as e:
            ac.log("XyroDevice %s" % e)
            ac.console(e)
        
        return packed_packet
        
    def generateInnerPacket(self, packetType):
        packed_data = b'\x00'
        try:
            ubx_header = 0x62B5
            ubx_class = 0x39
            ubx_id = CLASS_ID_ALIVE
            ubx_length = 92
            ubx_checksum = 0
            
            ubx_iTOW = int((time.time()+259200)*1000)%604800000 # GPS time of week in ms
            [ubx_year, ubx_month, ubx_day, ubx_hour, ubx_min, ubx_sec] = time.gmtime()[0:6]
            ubx_valid = 0xff
            ubx_tAcc = 10
            ubx_nano = 0
            ubx_fixType = 3 # 3D-fix
            ubx_flags = 0x33
            ubx_flags2 = 0xE0 # b_1110_0000
            ubx_numSV = 9
            [ubx_lon, ubx_lat, ubx_height] = self.getCarPosition()
            ubx_hMSL = ubx_height
            ubx_hAcc = 10
            ubx_vAcc = 10
            ubx_velN = 10
            ubx_velE = 10
            ubx_velD = 10
            ubx_gSpeed = int(info.physics.speedKmh*10000/36)
            ubx_headMot = int(((info.physics.heading + math.pi) * 180 / math.pi) * (10**5))
            ubx_sAcc = 10
            ubx_headAcc = 10 # TODO
            ubx_pDOP = 10
            ubx_reserved = 0
            ubx_headVeh = ubx_headMot
            ubx_magDec = 0
            ubx_magAcc = 0
            
            #ac.console("Car Coordinate : " + str(list(info.graphics.carCoordinates)))
            #ac.console("Calculated Lon(" + str(ubx_lon) + "),  Lat(" + str(ubx_lat)+")")
            
            packed_header = pack('HBBB', ubx_header, ubx_class, ubx_id, ubx_length)
            packed_payload = b'\x00'
            packed_checksum = b'\x00\x00'
            
            packed_data = b'\x00'
            
            if packetType == PACKET_ALIVE:
                fixFlag = 1
                fwVersion = "100B".encode().ljust(10,b'\0')
                powerSource = 1861
                runCount = 10
                connStat = 2
                
                packed_payload = pack('B', fixFlag) + pack('L', ubx_iTOW) + fwVersion + pack('H', powerSource) + pack('L', runCount) + pack('B', connStat)
                ubx_id = CLASS_ID_ALIVE
                ubx_length = len(packed_payload)
                packed_header = pack('HBBH', ubx_header, ubx_class, ubx_id, ubx_length)
                packed_checksum = self.calcUbxChecksum(ubx_class, ubx_id, pack('H', ubx_length) + packed_payload)
                packed_data = packed_header + packed_payload + packed_checksum
                
            elif packetType == PACKET_NAV_PVT:
                ubx_class = 0x01
                ubx_id = 0x07
                
                packed_payload = pack('L', ubx_iTOW) + pack('H', ubx_year) + pack('B', ubx_month) + pack('B', ubx_day) + pack('B', ubx_hour) + pack('B', ubx_min) + pack('B', ubx_sec) + pack('B', ubx_valid) + pack('L', ubx_tAcc) + pack('l', ubx_nano)
                packed_payload += pack('B', ubx_fixType) + pack('B', ubx_flags) + pack('B', ubx_flags2) + pack('B', ubx_numSV) + pack('l', ubx_lon) + pack('l', ubx_lat) + pack('l', ubx_height) + pack('l', ubx_hMSL) + pack('L', ubx_hAcc)
                packed_payload += pack('L', ubx_vAcc) + pack('l', ubx_velN) + pack('l', ubx_velE) + pack('l', ubx_velD) + pack('l', ubx_gSpeed) + pack('l', ubx_headMot) + pack('L', ubx_sAcc) + pack('L', ubx_headAcc) + pack('H', ubx_pDOP)
                packed_payload += pack('B', ubx_reserved) + pack('B', ubx_reserved) + pack('B', ubx_reserved) + pack('B', ubx_reserved) + pack('B', ubx_reserved) + pack('B', ubx_reserved) + pack('l', ubx_headVeh) + pack('h', ubx_magDec) + pack('H', ubx_magAcc)
                ubx_length = len(packed_payload)
                packed_header = pack('HBBH', ubx_header, ubx_class, ubx_id, ubx_length)
                packed_checksum = self.calcUbxChecksum(ubx_class, ubx_id, pack('H', ubx_length) + packed_payload)
                packed_data = packed_header + packed_payload + packed_checksum
            elif packetType == PACKET_START:
                pass
            else:
                packed_data = pack('HBBH', ubx_header, ubx_class, ubx_id, ubx_length)
        except Exception as e:
            ac.console(e)
        
        return packed_data
        
        
    def calcUbxChecksum(self, ubx_class, ubx_id, payload):
        # payload includes length and actual payload
        check1 = (ubx_class + ubx_id) % 256
        check2 = ((2*ubx_class) + ubx_id) % 256
        
        for i in range(0,len(payload)):
            check1 = (check1 + payload[i]) % 256
            check2 = (check1 + check2) % 256
            
        return pack('BB',check1,check2)
        
    def getDeviceTick(self):
        now = time.time()
        diff = now - self.time_device_start
        return int(diff*1000)%0x100000000
        
    def getCarPosition(self):
        position_in_ac = list(info.graphics.carCoordinates)
        position_in_gps = self.coordinateCovert(position_in_ac)
        return position_in_gps
        
    def coordinateCoverterInit(self):
        # 용인
        [self.x0, self.y0] = [-652.9, 90.9]
        [self.x0p, self.y0p] = [127.204706, 37.2978546]
        self.scale_factor = 90346.23362247727
        self.theta_rad = 0.00463278692
        
    def coordinateCovert(self, point):
        x = point[0]
        y = -point[2]
        height = point[1]
        
        xp = (math.cos(self.theta_rad) * (x-self.x0) + math.sin(self.theta_rad) * (y-self.y0)) / self.scale_factor + self.x0p
        yp = (-math.sin(self.theta_rad) * (x-self.x0) + math.cos(self.theta_rad) * (y-self.y0)) / self.scale_factor + self.y0p
        
        return [round(xp*(10**7)), round(yp*(10**7)), round(height*1000)]

