# This Python file uses the following encoding: utf-8
import requests
from WechartToken import WechartToken
from urlparse import urlparse, parse_qsl
from datetime import * 
import time
from MySQLHelper import MySQLHelper
import random
import time

class AutoSendMsg():
    def __init__(self, userName, pwd):
        self.userName = userName
        self.pwd = pwd
        self.isNotSendMsg = False
        self.msgUrl ='https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&lang=zh_CN'
    def getRequestInfo(self):
        wecharInfo = WechartToken(self.userName, self.pwd)
        self.headers = {
               'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
               'Referer':'https://mp.weixin.qq.com/cgi-bin/singlemsgpage',
               'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31',
               'X-Requested-With':'XMLHttpRequest'
               }
        self.cookies = dict(wecharInfo.cookie)
        self.token = wecharInfo.token
        
    def getInfoContent(self):
        self.sqlHelper = MySQLHelper('101.1.16.50','s559384db0','995y455y','s559384db0');
        
        startTimeStamp =  datetime.now() + timedelta(hours=-7)
        endTimeStamp = datetime.now()  + timedelta(hours=1)
        startTime = datetime(startTimeStamp.year, startTimeStamp.month, startTimeStamp.day, startTimeStamp.hour).strftime("%Y-%m-%d %H:%M:%S")
        endTime = datetime(endTimeStamp.year, endTimeStamp.month, endTimeStamp.day, endTimeStamp.hour).strftime("%Y-%m-%d %H:%M:%S")
        timeCondition = "saveTime between '" + startTime + "' and '" + endTime + "'"
        sqlStr = "select * from tblJobInfo where  " + timeCondition + " order by id desc limit 24"
        print sqlStr
        temptInfoList = self.sqlHelper.queryAll(sqlStr)
        if len(temptInfoList) == 0:
            self.isNotSendMsg = True
            return
        resultContent = ""
        for index, value in enumerate(temptInfoList):
            if index % 2 == 1:
                contentUrl = "http://campus4me.net/showMsgContent.php?msgId=" + value["id"]
                resultContent += "名称：" + value["title"] + "<a href=\"" + contentUrl +"\">[查看详情]</a>\n\n"
        self.resultContent = resultContent + "亲，记得回复‘h’显示更多帮助哦！！"
        print self.resultContent
        
    def sendMsg(self):
        sqlUserFakeId = "select fakeId from tblUserInfo"
        self.getInfoContent()
        print "isNotSendMsg: " + str(self.isNotSendMsg)
        if self.isNotSendMsg == True:
            return
        self.getRequestInfo()
        fakeIdList = self.sqlHelper.queryAll(sqlUserFakeId)
        sendMsg = {
               'type':1,
               'error':False,
               'tofakeid':'',
               'token':self.token,
               'content': self.resultContent,
               'ajax':1
               }
        print sendMsg
        sendedUser = []
        hasSendedUser = []
        print len(hasSendedUser)

        for index, infoItem in enumerate(fakeIdList):
            if infoItem["fakeId"] != "31164395" and infoItem["fakeId"] not in hasSendedUser:
            #if infoItem["fakeId"] == "520181815":
                sendMsg.update({'tofakeid':infoItem["fakeId"]})
                sendedUser.append(infoItem["fakeId"])
                print sendedUser
                responseMsg = requests.post(self.msgUrl, data = sendMsg, headers = self.headers,cookies = self.cookies);
                print responseMsg.content
        print sendedUser
            
msgSender = AutoSendMsg("85770253@qq.com", "44137b278ed88938e29626e010e8e159")
#msgSender.getInfoContent()
msgSender.sendMsg()
            #responseMsg = requests.post('https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&lang=zh_CN', data = sendMsg, headers = headers,cookies = dict(wecharInfo.cookie));
            #print responseMsg.content
 
    