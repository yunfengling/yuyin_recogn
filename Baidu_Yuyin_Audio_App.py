#!/usr/bin/env python3
#encoding=utf-8
import threading
import time
import random
 
import wx
import wx.lib.newevent
 
ItemActivated, EVT_ITEM_ACTIVATED = wx.lib.newevent.NewEvent()



# NOTE: this example requires PyAudio because it uses the Microphone class
import socket   #for sockets
import sys  #for exit
import speech_recognition as sr


import sys
import struct
import json
reload(sys)
sys.setdefaultencoding('gbk')

import wave
import urllib, urllib2, pycurl
import base64
import json

ANY ="127.0.0.1"# 'localhost' #
SENDERPORT = 18430

MCAST_ADDR ="127.0.0.1" # '224.1.1.1' #'224.168.2.9'   #
MCAST_PORT = 18432

bufBaiduResults = ''

## get access token by api key &amp; secret key
## 获得token，需要填写你的apikey以及secretkey
def get_token():
    apiKey = "l1i28xGUGlySxbEKk96utOCd"
    secretKey = "609f34eabe98e1d7cce9d46702230387"

    #auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&amp;client_id=" + apiKey + "&amp;client_secret=" + secretKey;
    auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey;
    res = urllib2.urlopen(auth_url)
    json_data = res.read()
    print "json_data", json_data
    return json.loads(json_data)['access_token']

def dump_res(buf):
    print ".....test buf...."
    #print (buf).encode('gbk')
    global bufBaiduResults
    bufBaiduResults = buf
    print (buf)


## post audio to server
def use_cloud(token, fileName):
    #pathWavefile = r"D:/SpeechRecog/BaiduTest/2016-09-25_22_57_34.wav"
    pathWavefile = fileName
    print u"录音文件名".encode('gbk')
    fp = wave.open(pathWavefile, 'rb')#录音文件名
    ##已经录好音的语音片段
    nf = fp.getnframes()
    f_len = nf * 2
    audio_data = fp.readframes(nf)

    cuid = "8625268" #你的产品id
    srv_url = 'http://vop.baidu.com/server_api' + '?cuid=' + cuid + '&token=' + token
    '''
    http_header = [
        'Content-Type: audio/pcm; rate=8000',
        'Content-Length: %d' % f_len
    ]
    '''
    http_header = [
        'Content-Type: audio/wav; rate=16000',
        'Content-Length: %d' % f_len
    ]

    c = pycurl.Curl()
    print ".....test 1...."
    c.setopt(pycurl.URL, str(srv_url)) #curl doesn't support unicode
    #c.setopt(c.RETURNTRANSFER, 1)
    c.setopt(c.HTTPHEADER, http_header)   #must be list, not dict
    c.setopt(c.POST, 1)
    c.setopt(c.CONNECTTIMEOUT, 30)
    c.setopt(c.TIMEOUT, 30)
    c.setopt(c.WRITEFUNCTION, dump_res)
    c.setopt(c.POSTFIELDS, audio_data)
    c.setopt(c.POSTFIELDSIZE, f_len)
    strTest = c.perform() #pycurl.perform() has no return val

    print ".....Done...."

'''
if __name__ == "__main__":
    token = get_token()
    #获得token
    use_cloud(token)
    #进行处理，然后

'''

def ParseStringFromBaidu(buffer):
    """
    baidu server returns a JSON string.
    To parse the JSON string to get status and results.
    """
    inforResults = json.loads(bufBaiduResults, encoding='gbk')
    if('success.' in inforResults['err_msg']):
        strRecognizedWords = inforResults['result'][0]
        isSuccess = True
    else:
        strRecognizedWords = "Failed this time!"
        isSuccess = False
    return isSuccess, strRecognizedWords


def SendData2Receiver(senderSocket, strRecognizedWords):
    buf2Send = struct.pack('<i', 1002)
    strResults = r"发送指令%s ......................."%(strRecognizedWords)
    msg2Send = bytearray(buf2Send + strResults)
    try :
        #Set the whole string
        senderSocket.sendto(msg2Send,  (MCAST_ADDR, MCAST_PORT))
        print msg2Send, "is sent.....s", 'to',  (MCAST_ADDR, MCAST_PORT)
    except socket.error, msg:
        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    return


##################################################
class BaiduOnlineRecognitionThread(threading.Thread):

    def __init__(self, mypanel, range_):
        self.mypanel = mypanel
        self.range = range_
        threading.Thread.__init__(self)
        return

    def run(self):
        saveout = sys.stdout
        fsock = open('out.log', 'w')
        sys.stdout = fsock

        fsockerr = open('error.log', 'w')
        sys.stderr = fsockerr

        # create dgram udp socket
        try:
            senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            senderSocket.bind((ANY, SENDERPORT)) #绑定发送端口到SENDERPORT，即此例的发送端口为1501

            ttl_bin = struct.pack('@i', 1)
            senderSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin) #设置使用多播发送
        except socket.error:
            print 'Failed to create socket'
            sys.exit()

        strTest = u"发送指令  ..............................".encode(encoding='gbk')
        #print strTest.decode(encoding='gbk')
        buf2Send = struct.pack('<i', 1002)
        msg2Send = bytearray(buf2Send + strTest)
        #print msg2Send
        #############################################
        token = get_token()

        wx.PostEvent(self.mypanel, ItemActivated(data=1009, thread=threading.current_thread()))

        count = 0
        it = 0
        fileName = "audio_microphone-results.wav"  #TODO:
        while True:

            timeBegin = time.time()

            use_cloud(token, fileName)  ##shibie
            ###########################################
            ### send results
            inforResults =json.loads(bufBaiduResults)
            if('success.' in inforResults['err_msg']):
                strRecognizedWords = inforResults['result'][0]
            else:
                strRecognizedWords = "Failed this time!"
            #strResults = r"发送指令 %s .........................................."%(strRecognizedWords)
            strResults = strRecognizedWords.encode(encoding='gbk') + u"..以上是识别结果  ..............................".encode(encoding='gbk')
            buf2Send = struct.pack('<i', 1002)
            msg2Send = bytearray(buf2Send + strResults)

            try :
                #Set the whole string
                senderSocket.sendto(msg2Send,  (MCAST_ADDR, MCAST_PORT))
                print strResults, "is sent.....s", 'to',  (MCAST_ADDR, MCAST_PORT)
            except socket.error, msg:
                print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                sys.exit()
            #print '____________________________________________\n'
            timeEnd = time.time()
            strRuntime = " Runtime=%.1fsec"%(timeEnd - timeBegin)
            wx.PostEvent(self.mypanel,
                         ItemActivated(data=1011, #random.randint(*self.range),
                                       thread=threading.current_thread()))
            wx.PostEvent(self.mypanel,
                         ItemActivated(data ='Results= '.encode('gbk') + strRecognizedWords +'  Sent to:' + MCAST_ADDR + ':' + str(MCAST_PORT) + strRuntime, #random.randint(*self.range), + MCAST_ADDR+ MCAST_PORT
                                       thread=threading.current_thread()))
            count += 1
            it += 1
        return


#################################################################
class AudioThread(threading.Thread):

    def __init__(self, mypanel, range_):
        self.mypanel = mypanel
        self.range = range_
        threading.Thread.__init__(self)
        return

    def run(self):


        '''
        # create dgram udp socket
        try:
            senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            senderSocket.bind((ANY, SENDERPORT)) #绑定发送端口到SENDERPORT，即此例的发送端口为1501

            ttl_bin = struct.pack('@i', 1)
            senderSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin) #设置使用多播发送
        except socket.error:
            print 'Failed to create socket'
            sys.exit()

        strTest = u"发送指令  ..............................".encode(encoding='gbk')
        #print strTest.decode(encoding='gbk')
        buf2Send = struct.pack('<i', 1002)
        msg2Send = bytearray(buf2Send + strTest)
        #print msg2Send
        #############################################
        '''
        token = get_token()

        wx.PostEvent(self.mypanel, ItemActivated(data=1009, thread=threading.current_thread()))

        ############  monitoring microphone, and record voice
        count = 0
        it = 0
        r = sr.Recognizer()
        while True:

            with sr.Microphone() as source:
                #print("Say something!")
                audio = r.listen(source)
            #print "recording is done", it

            timeBegin = time.time()

            # write audio to a WAV file
            fileName = "audio_microphone-results.wav"
            with open(fileName, "wb") as f:
                f.write(audio.get_wav_data())
            #print  "recording is done", it, "to: ", fileName

            wx.PostEvent(self.mypanel,
                         ItemActivated(data=1010, #random.randint(*self.range),
                                       thread=threading.current_thread()))
            ''''''
            use_cloud(token, fileName)  ##shibie
            ###########################################
            ### send results
            inforResults =json.loads(bufBaiduResults)
            if('success.' in inforResults['err_msg']):
                strRecognizedWords = inforResults['result'][0]
            else:
                strRecognizedWords = "Failed this time!"
            #strResults = r"发送指令 %s .........................................."%(strRecognizedWords)
            strResults = strRecognizedWords.encode(encoding='gbk') + u"..以上是识别结果  ..............................".encode(encoding='gbk')
            buf2Send = struct.pack('<i', 1002)
            msg2Send = bytearray(buf2Send + strResults)

            '''
            try :
                #Set the whole string
                senderSocket.sendto(msg2Send,  (MCAST_ADDR, MCAST_PORT))
                print strResults, "is sent.....s", 'to',  (MCAST_ADDR, MCAST_PORT)
            except socket.error, msg:
                print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                sys.exit()
            #print '____________________________________________\n'
            timeEnd = time.time()
            strRuntime = " Runtime=%.1fsec"%(timeEnd - timeBegin)
            wx.PostEvent(self.mypanel,
                         ItemActivated(data=1011, #random.randint(*self.range),
                                       thread=threading.current_thread()))
            wx.PostEvent(self.mypanel,
                         ItemActivated(data ='Results= '.encode('gbk') + strRecognizedWords +'  Sent to:' + MCAST_ADDR + ':' + str(MCAST_PORT) + strRuntime, #random.randint(*self.range), + MCAST_ADDR+ MCAST_PORT
                                       thread=threading.current_thread()))
            '''
            count += 1
            it += 1

class WorkerThread(threading.Thread):
 
    def __init__(self, mypanel, range_):
        self.mypanel = mypanel
        self.range = range_
        threading.Thread.__init__(self)
 
    def run(self):
        count = 0
        while count < 15:
            time.sleep(1)
            wx.PostEvent(self.mypanel,
                         ItemActivated(data=random.randint(*self.range),
                                       thread=threading.current_thread()))
            count += 1
 


class CommSocket():

    def __init__(self):
        self._socketSender = None
        #self.InitSocket()
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
            sys.exit(3)
            return 3

        strTest = u"发送指令  ..............................".encode(encoding='gbk')
        #print strTest.decode(encoding='gbk')
        buf2Send = struct.pack('<i', 1002)
        msg2Send = bytearray(buf2Send + strTest)
        #print msg2Send
        #############################################
        #token = get_token()
        self._socketSender = senderSocket

        #wx.PostEvent(self.mypanel, ItemActivated(data=1009, thread=threading.current_thread()))
        return 0

    def GetSocket(self):
        return self._socketSender



class MyPanel(wx.Panel):
 
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
 

 
        self.mystatic_text = wx.StaticText(self, -1, label="In Main Thread. Waiting for ready......")
        self.sizer.Add(self.mystatic_text)
        self.Bind(EVT_ITEM_ACTIVATED, self.on_item_activated)
 
        self.SetSizerAndFit(self.sizer)

        ################
        commSocket = CommSocket()
        status = commSocket.InitSocket()
        if(0 == status):
            self.update_text_ui("\n Now, ready to use.") # 已UDP连接完成，通讯正常使用。
        else:
            self.update_text_ui("\n Error:  Socket error !!! .")
        self._commSocket = commSocket

        ###################################################################
        #worker_thread1 = WorkerThread(mypanel=self, range_=(1, 100))
        #worker_thread1.daemon = True
        worker_thread2 = AudioThread(mypanel=self, range_=(1000, 2000))
        worker_thread2.daemon = True
        #worker_thread1.start()
        worker_thread2.start()

        print "Init is done..."
        return

    def update_text_ui(self, strMsg):
        old_label = self.mystatic_text.GetLabel()
        self.mystatic_text.SetLabel(old_label + strMsg)
        return

    def on_item_activated(self, evt):
        old_label = self.mystatic_text.GetLabel()
        if(evt.data == 1010):
            strEvent = "\n->Event From %s: %s" % (evt.thread, 'audio recorded.')
        elif(evt.data == 1011):
            strEvent = "\n->Event From %s: %s" % (evt.thread, 'Baidu recognization results')
        elif(evt.data == 1009):
            strEvent = "\n->Event From %s: %s" % (evt.thread, 'Ready to use!')
        else:
            strEvent = "\n->Event From %s: %s" % (evt.thread, evt.data)
        self.update_text_ui(strEvent)
        return
 
 
if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None, title="wx.PostEvent Example with Threads",
                     size=(850, 400))
    MyPanel(frame)
    frame.CenterOnScreen()
    frame.Show()
    app.MainLoop()