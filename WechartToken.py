# This Python file uses the following encoding: utf-8
import requests
import chardet
import re
import cStringIO
import base64
from MyHTMLParser import MyHTMLParser
from MySQLHelper import MySQLHelper
from urlparse import urlparse, parse_qsl

class WechartToken:
    def __init__(self, userName, pwd):
        self.userName = userName
        self.pwd = pwd
        self.headers = {
               'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
               'Referer':'https://mp.weixin.qq.com/cgi-bin/singlemsgpage',
               'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31',
               'X-Requested-With':'XMLHttpRequest'
               }
        self.baseURI = "https://mp.weixin.qq.com/cgi-bin/"
        self.requestURI = self.baseURI + "login?lang=zh_CN"
        self.contactURI = self.baseURI + "getcontactinfo?t=ajax-getcontactinfo&lang=zh_CN"
        self.usrListURI = self.baseURI + "contactmanagepage?t=wxm-friend&lang=zh_CN&pagesize=550"
        self.imageURI = self.baseURI + "uploadmaterial?cgi=uploadmaterial&type=2&t=iframe-uploadfile&lang=zh_CN"
        self.doRequest()
    def doRequest(self):
         params = {
             'username': self.userName,
             'pwd': self.pwd,
             'imgcode':'',
             'f':'json',
             'register':0
         }
         responseData = requests.post(self.requestURI, data = params)
         self.responseData = responseData
         self.getToken()
         self.getCookie()
         
    def getToken(self):
       responseContent = eval(self.responseData.content)
       errMsg = responseContent["ErrMsg"]
       token = parse_qsl(urlparse(errMsg)[4])[2][1]
       self.token = token
       
    def getCookie(self):
        cookies = self.responseData.cookies
        cookie = {
              "remember_acct": self.userName,
              "hasWarningUser": 1,
              "o_cookie": "85770253",
              "ptui_loginuin": self.userName
              }
        for c in cookies:
            cookie[c.name] = c.value
        self.cookie = cookies
        
    def getFormId(self, index = 0):
        imageURI = self.imageURI + "&token=" +self.token + "&formId=1" + str(index + 1)
        payLoad = {
                   "name":"uploadfile",
                   "filename":"test.jpg"
                   }
        #f = open('tmpt.jpg','wb')
        #f.write(requests.get("http://tp4.sinaimg.cn/1788752195/180/5626270465/1").content)
        #f.close() 
        files = {'uploadfile':  open("./images/" + str(index + 1) + ".jpg", "rb")}
        responseData = requests.post(imageURI, files = files,  cookies = dict(self.cookie));
        outer = re.compile("formId, '(\d+)'")
        m = outer.search(responseData.content)
        print m.group(1)
        return m.group(1)
    
    def getUserFakeId(self):
        userListUrl = self.usrListURI + "&token=" +self.token
        responseData = requests.get(userListUrl, headers = self.headers, cookies = dict(self.cookie))
        contentStr = MyHTMLParser(responseData.content).print_contents("script", ("id", "json-friendList"))
        fakeIdList = []
        contentList = eval(contentStr)
        for item in contentList:
            fakeIdList.append(item["fakeId"])
        self.fakeIdList = fakeIdList
        
    def getContact(self):
        contactList = []
        sqlHelper = MySQLHelper('101.1.16.46','s559384db0','995y455y','s559384db0');
        dbUserList = sqlHelper.queryAll("SELECT fakeId FROM tblUserInfo ")
        dbFakeIdList = []
        for user in dbUserList:
            dbFakeIdList.append(user["fakeId"])
        print dbFakeIdList
        print self.fakeIdList[0:2]
        for fakeId in self.fakeIdList:
            if fakeId  not in dbFakeIdList:
                print fakeId
                self.pushWelcomeMsg(fakeId)
                userContact = self.getUserInfo(fakeId)
                encoding = chardet.detect(userContact)['encoding']
                if userContact != 'utf-8':
                    userContact = userContact.decode(encoding, 'replace').encode('utf-8')
                    contactList.append(userContact)
        for value in contactList:
            insertValue = eval(value)
            del insertValue["Groups"]
            sqlHelper.insert("tblUserInfo", insertValue)
            
    def pushWelcomeMsg(self, toFakeId):
        sendMsg = {
               'type':1,
               'error':False,
               'tofakeid':'',
               'token':self.token,
               'content':"亲，回复‘h’可以显示更多帮助哦！！",
               'ajax':1
               }
        headers = {
               'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
               'Referer':'https://mp.weixin.qq.com/cgi-bin/singlemsgpage',
               'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31',
               'X-Requested-With':'XMLHttpRequest'
               }
        sendMsg.update({'tofakeid':toFakeId})
        responseMsg = requests.post('https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&lang=zh_CN', data = sendMsg, headers = headers,cookies = dict(self.cookie))
        print responseMsg.content

        
        
    def getUserInfo(self, fakeId):
        infoUrl = self.contactURI + "&fakeid=" + fakeId
        sendMsg = {
                   "token":self.token,
                   "ajax":1
                   }
        contactInfo = requests.post(infoUrl, data = sendMsg, headers = self.headers, cookies = dict(self.cookie));
        return contactInfo.content