#!/usr/bin/env python3
#encoding=utf-8

import socket
import struct

ANY ="127.0.0.1"# 'localhost' #
SENDERPORT = 18430

MCAST_ADDR ="127.0.0.1" # '224.1.1.1' #'224.168.2.9'   #
MCAST_PORT = 18432

class DataUdpSender():

    def __init__(self):
        self._socketSender = None
        return

    def InitSocket(self):
        # create dgram udp socket
        try:
            senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            senderSocket.bind((ANY, SENDERPORT)) #绑定发送端口到SENDERPORT，即此例的发送端口为1501

            ttl_bin = struct.pack('@i', 1)
            senderSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin) #设置使用多播发送
        except socket.error:
            print 'Failed to create socket'
            return 3
        self._socketSender = senderSocket
        return 0

    def GetSocket(self):
        return self._socketSender

    def SendData(self, dataBuf):
        ret = 0
        senderSocket = self.GetSocket()
        try :
            #Set the whole string
            senderSocket.sendto(dataBuf,  (MCAST_ADDR, MCAST_PORT))
            #print strResults, "is sent.....s", 'to',  (MCAST_ADDR, MCAST_PORT)
        except socket.error, msg:
            print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            ret = -1
        print 'Sending is done ____________________________________________\n'
        return ret
