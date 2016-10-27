#!/usr/bin/env python3
#encoding=utf-8

import threading
import time
import random

import wx
import wx.lib.newevent
ItemActivated, EVT_ITEM_ACTIVATED = wx.lib.newevent.NewEvent()

# NOTE: this example requires PyAudio because it uses the Microphone class
import speech_recognition as sr
import struct
import sys
import json
reload(sys)
sys.setdefaultencoding('gbk')

import wave
import urllib, urllib2, pycurl
import base64
import json


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
    #print (buf).encode('gbk')
    global bufBaiduResults
    bufBaiduResults = buf
    print " Buf received from baidu: \n" #, (buf)
    return


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

    http_header = [
        'Content-Type: audio/wav; rate=16000',
        'Content-Length: %d' % f_len
    ]

    c = pycurl.Curl()
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
    print ".... post audio to server is.Done...."


def ParseStringFromBaidu(buffer):
    """
    baidu server returns a JSON string.
    To parse the JSON string to get status and results.
    """
    try:
        inforResults = json.loads(bufBaiduResults, encoding='gbk')
    except ValueError:
        print "ValueError ParseStringFromBaidu"

    if('success.' in inforResults['err_msg']):
        strRecognizedWords = inforResults['result'][0]
        isSuccess = True
    else:
        strRecognizedWords = "Failed this time!"
        isSuccess = False
    return isSuccess, strRecognizedWords


##################################################
class BaiduOnlineRecognitionThread(threading.Thread):

    _STATUS_RECOGN_IDLE = 0
    _STATUS_RECOGN_PROCESSING = 1

    def __init__(self, mypanel, range_):
        self.mypanel = mypanel
        self.range = range_
        threading.Thread.__init__(self)
        self._token = get_token()  #获得token
        self._isNewAudioRecorded = False
        self._nAudioIndex = 0
        self._strBaiduResults = ''
        self._statusRecogn = self._STATUS_RECOGN_IDLE
        return

    def ClearNewAudioFlag(self):
        self._isNewAudioRecorded = False
        self._statusRecogn = self._STATUS_RECOGN_IDLE
        return

    def SetNewAudioFlag(self, audioIndex):
        ret = 0
        if(self._statusRecogn == self._STATUS_RECOGN_IDLE):
            self._isNewAudioRecorded = True
            self._nAudioIndex = audioIndex
        else:
            ret = self._statusRecogn
        return ret

    def GetAudioRecordIndex(self):
        return self._nAudioIndex

    def GetToken(self):
        return self._token

    def GetResultsString(self):
        return self._strBaiduResults

    def SetResultsString(self, strResults):
        self._strBaiduResults = strResults
        return

    def run(self):
        #############################################
        token = self.GetToken()

        count = 0
        it = 0
        fileName = "audio_microphone-results.wav"  #TODO:
        print "run baidu cloud"

        while True:
            if self._isNewAudioRecorded:
                self._statusRecogn = self._STATUS_RECOGN_PROCESSING
                print "new audio available to test..."
                timeBegin = time.time()

                ##shibie #进行处理，然后
                use_cloud(token, fileName)

                ###########################################
                ### send results
                inforResults =json.loads(bufBaiduResults)
                if('success.' in inforResults['err_msg']):
                    strRecognizedWords = inforResults['result'][0]
                    strResults = strRecognizedWords
                else:
                    strRecognizedWords = "Failed this time!"
                    strResults = ''
                self.SetResultsString(strResults)

                print "Ready to send in baidu thread:",strRecognizedWords

                timeEnd = time.time()
                strRuntime = "(AudioID=%d), Runtime=%.1fsec"%(self.GetAudioRecordIndex(), timeEnd - timeBegin)

                wx.PostEvent(self.mypanel,
                             ItemActivated(data=1011, #random.randint(*self.range),
                                           thread=threading.current_thread()))
                wx.PostEvent(self.mypanel,
                                #ItemActivated(data ='Results= '.encode('gbk') + strRecognizedWords +'  Sent to:' + MCAST_ADDR + ':' + str(MCAST_PORT) + strRuntime, #random.randint(*self.range), + MCAST_ADDR+ MCAST_PORT
                                ItemActivated(data ='Results= '.encode('gbk') + strRecognizedWords  + strRuntime, #random.randint(*self.range), + MCAST_ADDR+ MCAST_PORT
                                thread=threading.current_thread()))

                self.ClearNewAudioFlag()
        return

#################################################################
class AudioThread(threading.Thread):

    def __init__(self, mypanel, range_):
        self.mypanel = mypanel
        self.range = range_
        self._nCountAudioRecorded = 0
        threading.Thread.__init__(self)
        return

    def GetAudioRecordCount(self):
        return self._nCountAudioRecorded

    def run(self):
        ############  monitoring microphone, and record voice
        count = 0
        it = 0
        r = sr.Recognizer()

        while True:
            with sr.Microphone() as source:
                #print("Say something!")
                audio = r.listen(source)
            #print "recording is done", it

            # write audio to a WAV file
            fileName = "audio_microphone-results.wav"
            with open(fileName, "wb") as f:
                f.write(audio.get_wav_data())
            print  "recording is done", it, "to: ", fileName

            self._nCountAudioRecorded += 1

            wx.PostEvent(self.mypanel,
                         ItemActivated(data=1010, #random.randint(*self.range),
                                       thread=threading.current_thread()))
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

