#!/usr/bin/env python3
#encoding=utf-8

import wx
import sys

reload(sys)
sys.setdefaultencoding('gbk')

################################
from DataUdpSender import DataUdpSender
#from Threads import AudioThread, BaiduOnlineRecognitionThread
from Threads import *

VERSION_MAJOR = 1
VERSION_MINOR = 2

class MyPanel(wx.Panel):
 
    def __init__(self, parent):
        '''
        ########
        saveout = sys.stdout
        fsock = open('out.log', 'w')
        sys.stdout = fsock

        fsockerr = open('error.log', 'w')
        sys.stderr = fsockerr
        '''
        #############
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
 
        self.mystatic_text = wx.StaticText(self, -1, label="In Main Thread. Waiting for ready......")
        self.sizer.Add(self.mystatic_text)
        self.Bind(EVT_ITEM_ACTIVATED, self.on_item_activated)
 
        self.SetSizerAndFit(self.sizer)

        ################
        commDataUdpSender = DataUdpSender()
        status = commDataUdpSender.InitSocket()
        if(0 == status):
            self.update_text_ui("\n Now, UDP socket ready to use.") # 已UDP连接完成，通讯正常使用。
        else:
            self.update_text_ui("\n Error: UDP Socket error !!! .")
        self._commSocket = commDataUdpSender

        ###################################################################
        #worker_thread1 = WorkerThread(mypanel=self, range_=(1, 100))
        #worker_thread1.daemon = True
        worker_thread2 = AudioThread(mypanel=self, range_=(1000, 2000))
        worker_thread2.daemon = True
        #worker_thread1.start()
        worker_thread2.start()
        self._audioRecordThread = worker_thread2

        baiduThread = BaiduOnlineRecognitionThread(mypanel=self, range_=(1000, 2000))
        baiduThread.daemon = True
        baiduThread.start()
        self._baiduRecognThread = baiduThread
        print "Init is done..."
        return

    def GetCommObject(self):
        return self._commSocket

    def update_text_ui(self, strMsg):
        old_label = self.mystatic_text.GetLabel()
        nNewLines = old_label.count(r'->')
        if(nNewLines > 28):
            old_label = ''
        self.mystatic_text.SetLabel(old_label + strMsg)
        return

    def on_item_activated(self, evt):
        old_label = self.mystatic_text.GetLabel()
        if(evt.data == 1010):
            nAudioIndex = self._audioRecordThread.GetAudioRecordCount()
            strEvent = "\n->Event From %s: %s (audio ID=%d)" % (evt.thread, 'Audio recorded. ', nAudioIndex)

            ## trigger baidu recognition
            self._baiduRecognThread.SetNewAudioFlag(nAudioIndex)

        elif(evt.data == 1011):
            strEvent = "\n->Event From %s: %s" % (evt.thread, 'Baidu recognization results')

            # send data to receiver.
            strResults = self._baiduRecognThread.GetResultsString()
            if(strResults):
                strResults = strResults.encode(encoding='gbk') + u"..以上是识别结果  ..............................".encode(encoding='gbk')
                buf2Send = struct.pack('<i', 1002)
                msg2Send = bytearray(buf2Send + strResults)
                print "Ready to send in GUI...... "
                status = self.GetCommObject().SendData(msg2Send)
                if(status):
                    strEvent += "\n Error in UDP data sending... "
                else:
                    strEvent += "\n -----> UDP data is sent... "

        elif(evt.data == 1009):
            strEvent = "\n->Event From %s: %s" % (evt.thread, 'Ready to use!')

        else:
            strEvent = "\n->Event From %s: %s" % (evt.thread, evt.data)
        self.update_text_ui(strEvent)
        return
 
##################################################################
if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None, title="VoiceRecognition V%d.%d"%(VERSION_MAJOR, VERSION_MINOR),
                     size=(850, 400))
    MyPanel(frame)
    frame.CenterOnScreen()
    frame.Show()
    app.MainLoop()