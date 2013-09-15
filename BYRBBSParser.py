# This Python file uses the following encoding: utf-8
from bs4 import BeautifulSoup
import requests
import chardet
import time
from datetime import * 
import re
from MySQLHelper import MySQLHelper

class TelnetContent():
    def __init__(self, urlItem):
        self.headers = {'X-Requested-With':'XMLHttpRequest'}
        responseContent = requests.get(urlItem["url"],  headers = self.headers).content
        encoding = chardet.detect(responseContent)['encoding']
        if responseContent != 'utf-8':
            responseContent = responseContent.decode(encoding, 'replace').encode('utf-8')
        self.bScontent = BeautifulSoup(''.join(responseContent))
        self.parserContent()
    def parserContent(self):
        inner_str = str(self.bScontent.select(".a-content")[0])
        splitFlag = "站内"
        infoList = inner_str.split(splitFlag)
        tmptContent = infoList[1]
        tmptContent = unicode(tmptContent.split("--")[0]).encode('utf-8')
        self.content = tmptContent
        
class BYRParser():
    def __init__(self, content, existInfoIdList, urlItem):
        self.isContinue = True
        self.existInfoIdList = existInfoIdList
        self.urlItem = urlItem
        self.bScontent = BeautifulSoup(''.join(content)) 
        self.flag =  ["校招", "实习生", "Intern", "intern"]
    def getContent(self, selectors):
        trList = self.bScontent.select("tr")
        infoList = []
        for tr in trList:
            self.isSave = True
            self.tmplContent = {}
            for key, value in selectors.items():
                if tr.select(value)[0] is not None:
                    self.tmplContent.update(getattr(self, key)(tr.select(value)[0]))
            if self.isSave == True :
                infoList.append(self.tmplContent)
        self.infoList = infoList
    def parseAnchor(self, anch):
        anchor = anch.a
        if anchor is not None:
            href = self.urlItem["contentUrl"] + anchor['href']
            infoId = anchor['href'].split("/")[3]
            title = anchor.string
            if any(keyword in title for keyword in self.flag) and (infoId  not in self.existInfoIdList):
                self.existInfoIdList.append(infoId)
                content = TelnetContent({
                                         "url":href
                                        }).content
                return {
                         "infoId": infoId,
                         "href":  href,
                         "bbsId": self.urlItem["bbsId"],
                         "saveTime":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         "title": title,
                         "content": content,
                        }
            else:
                self.isSave = False
                return {}
        else:
            self.isSave = False
            return {}
                
                
    def parserTimeStamp(self, timeStamp):
        publishTime = timeStamp.string
        yesterdayTime =  datetime.now() - timedelta(days=1)
        yesterday = date(yesterdayTime.year, yesterdayTime.month, yesterdayTime.day)
        if str(publishTime) == str(yesterday):
            self.isContinue = False
            self.isSave = False
            return {}
        elif publishTime.find(":") is not -1:
             return {"publishTime": publishTime};
        else:
            self.isSave = False
            return {}
        
        
class BYRBBSParser():
    def __init__(self, urls):
        self.urls = urls
        self.headers = {'X-Requested-With':'XMLHttpRequest'}
        self.finalInfo = []
        startTimeStamp =  datetime.now()
        endTimeStamp = datetime.now()+ timedelta(days=1)
        startTime = date(startTimeStamp.year, startTimeStamp.month, startTimeStamp.day).strftime("%Y-%m-%d %H:%M:%S")
        endTime = date(endTimeStamp.year, endTimeStamp.month, endTimeStamp.day).strftime("%Y-%m-%d %H:%M:%S")
        self.timeCondition = "saveTime between '" + startTime + "' and '" + endTime + "'"
    def getAllContent(self):
        sqlHelper = MySQLHelper('101.1.16.50','s559384db0','995y455y','s559384db0'); 
        if type(self.urls) == list:
            for urlItem in self.urls:
                sqlStr = "select infoId from tblJobInfo where bbsId = "+ urlItem["bbsId"] + " and " + self.timeCondition
                temptInfoList = sqlHelper.queryAll(sqlStr)
                self.existInfoIdList = []
                for infoDic in temptInfoList:
                    self.existInfoIdList.append(infoDic["infoId"])
                self.getContent(urlItem)
        else:
            sqlStr = "select infoId from tblJobInfo where bbsId = "+ str(self.urls["bbsId"]) + " and " + self.timeCondition
            temptInfoList = sqlHelper.queryAll(sqlStr)
            self.existInfoIdList = []
            for infoDic in temptInfoList:
                self.existInfoIdList.append(infoDic["infoId"])
            self.getContent(self.urls)
            
           
    def getContent(self, urlItem, pageNum = 0):
        responseContent = requests.get(urlItem["url"] + str(pageNum),  headers = self.headers).content
        encoding = chardet.detect(responseContent)['encoding']
        if responseContent != 'utf-8':
            responseContent = responseContent.decode(encoding, 'replace').encode('utf-8')
        parser = BYRParser(responseContent, self.existInfoIdList, urlItem)
        parser.getContent(urlItem["selector"])
        self.content = parser.bScontent
        self.finalInfo.extend(parser.infoList)
        if parser.isContinue == True:
            pageNum = pageNum + 1
            self.getContent(urlItem, pageNum)
        
        
