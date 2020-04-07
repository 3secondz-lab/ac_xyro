import euclid
import ac
import acsys
import math

import socket
from sim_info import info
from struct import *
from threading import Timer
import time


PACKET_ALIVE = 1
packettype = 0

CLASS_ALIVE = 0x00
CLASS_START = 0x01
CLASS_CAN = 0x04
CLASS_OBD_FAST = 0x05
CLASS_OBD_SLOW = 0x06
CLASS_OBD_DATA = 0x07
CLASS_SERVER_WIFI = 0x11
CLASS_STOP = 0x12
CLASS_OBD_PID = 0x13
CLASS_FW_UPDATE = 0x14
CLASS_FW_VERSION = 0x15
CLASS_RESET = 0x16




class XyroDevice(object):
    name = "player name"
    deviceOn = False
    destIP = "127.0.0.1"
    destPort = 59481
    localIP = "127.0.0.1"
    localPort = 59482
    message = ""
    sock = None
    
    serialNumber = 0
    
    sendAlivePacketRunning = False
    timerSendAlive = None
    timerSendAliveInterval = 2.0

    def __init__(self, serverIP, serverPort):
        ac.log("XyroDevice::__init__()")
        self.deviceOn = False
        self.destIP = serverIP
        self.destPort = serverPort
        

    def setup(self):
        ac.log("XyroDevice::setup()")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            self.sock.bind((self.localIP, self.localPort))
            self.sock.setblocking(0)
        except Exception as e:
            ac.log("XyroDevice::setup() %s" % e)

    def start(self):
        ac.log("XyroDevice::start()")
        self.setup()
        self.deviceOn = True

    def stop(self):
        ac.log("XyroDevice::stop()")
        self.sendAlivePacketStop()
        sock.close()
        self.deviceOn = False

    def sendInfo(self):
        # ac.log("XyroDevice::sendInfo()")
        if self.deviceOn == False:
            return
        try:
            ############ send data to server
            #message = "speed: " + str(int(info.physics.speedKmh))
            #self.sock.sendto(message.encode(), (self.destIP, self.destPort))
            # self.sock.sendto(self.generateUbxNavPvt(0), (self.destIP, self.destPort))
            pass
        except Exception as e:
            ac.log("XyroDevice::sendInfo() %s" % e)

    def recvInfo(self):
        recv_message = self.sock.recvfrom(1024)
        
        ######### process received command
        
        
        return recv_message[0]
    
    def isOn(self):
        return self.deviceOn
        
    def sendAlivePacketRun(self):
        self.sendAlivePacketRunning = False
        self.sendAlivePacketStart()
        
        # actual task
        try:
            if self.isOn() == True:
                self.sock.sendto(self.generateUbxNavPvt(PACKET_ALIVE), (self.destIP, self.destPort))
        except Exception as e:
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
        
        
    def generateUbxNavPvt(self, packettype):
        packed_data = 0
        try:
            ubx_header = 0x62B5
            ubx_class = 0x39
            ubx_id = 0x07
            ubx_length = 92
            ubx_checksum = 0
            
            ubx_iTOW = int((time.time()+259200)*1000)%604800000 # GPS time of week in ms
            # ubx_month = time.gmtime()[0]
            # ubx_day = 0
            # ubx_hour = 0
            # ubx_min = 0
            # ubx_sec = 0
            [ubx_year, ubx_month, ubx_day, ubx_hour, ubx_min, ubx_sec] = time.gmtime()[0:6]
            ubx_valid = 0xff
            ubx_tAcc = 10
            ubx_nano = 0
            ubx_fixType = 3 # 3D-fix
            ubx_flags = 33
            ubx_flags2 = 0xE0 # b_1110_0000
            ubx_numSV = 9
            ubx_lon = 0     # TODO
            ubx_lat = 0     # TODO
            ubx_height = 0  # TODO
            ubx_hMSL = 0    # TODO
            ubx_hAcc = 10
            ubx_vAcc = 10
            ubx_velN = 10
            ubx_velE = 10
            ubx_velD = 10
            ubx_gSpeed = int(info.physics.speedKmh*100000/3600)  # TODO
            ubx_headMot = 0 # TODO
            ubx_sAcc = 10
            ubx_headAcc = 10 # TODO
            ubx_pDOP = 10
            ubx_reserved1 = 0
            ubx_headVeh = ubx_headMot
            ubx_magDec = 0
            ubx_magAcc = 0
            
            # ac.console(str(ubx_gSpeed))
            
            packed_header = pack('HBBB', ubx_header, ubx_class, ubx_id, ubx_length)
            packed_payload = b'\x00'
            packed_checksum = b'\x00\x00'
            
            packed_data = 0
            
            if packettype == PACKET_ALIVE:
                packed_payload = pack('L',ubx_iTOW)
                ubx_class = CLASS_ALIVE
                ubx_length = len(packed_payload)
                packed_header = pack('HBBB', ubx_header, ubx_class, ubx_id, ubx_length)
                packed_checksum = self.calcUbxChecksum(ubx_class, ubx_id, packed_payload)
                packed_data = packed_header + packed_payload + packed_checksum
            else:
                packed_data = pack('HBBB', ubx_header, ubx_class, ubx_id, ubx_length)
        except Exception as e:
            ac.console(e)
        
        return packed_data
        
    def calcUbxChecksum(self, ubx_class, ubx_id, payload):
        
        check1 = (ubx_class + ubx_id) % 256
        check2 = ((2+ubx_class) + ubx_id) % 256
        
        for i in range(0,len(payload)):
            check1 = (check1 + payload[i]) % 256
            check2 = (check1 + check2) % 256
            
        return pack('BB',check1,check2)

