# This Python file uses the following encoding: utf-8
from MyHTMLParser import MyHTMLParser
from datetime import *  
import requests
import chardet
import re
import sys
import time
from MySQLHelper import MySQLHelper

reload(sys) 
sys.setdefaultencoding("UTF-8")

class TelnetBBSParser(MyHTMLParser):
        def __init__(self, html):
            print "1"
            MyHTMLParser.__init__(self, html)
        def getScriptContent(self, flag, tag):
            self.tag_stack = []
            self.tagName = tag
            self.flag = flag
            self.feed(self.html)
            return self.content
        def handle_starttag(self, tag, attrs):
            self.tag_stack.append(tag.lower())
        def handle_data(self, data):
            if len(self.tag_stack) and self.tag_stack[-1] == self.tagName:
                if data.find(self.flag) != -1:
                    self.content = data
                    
class TelnetContent():
    def __init__(self, urlItem):
        responseContent = requests.get(urlItem["url"]).content
        encoding = chardet.detect(responseContent)['encoding']
        if responseContent != 'utf-8':
            responseContent = responseContent.decode(encoding, 'replace').encode('utf-8')
        parser = TelnetBBSParser(responseContent)
        parser.getScriptContent(urlItem["contentFlag"], "script")
        print parser.content
        self.parserContent(urlItem, parser.content)
    def parserContent(self, urlItem, cont):
        outer = re.compile(urlItem["parseFlag"] + "\('(.+)'\)")
        m = outer.search(cont)
        if m is not None:
                inner_str = m.group(1)
                splitFlag = "站内"
                infoList = inner_str.split(splitFlag)
                temptContent = infoList[1]
                temptContent = unicode(temptContent.split("--")[0]).encode('utf-8')
                #linend = re.compile(r"\\n.*?\\n")
                #print linend.search(temptContent).groups(1)
                contenSplitList = temptContent.split('\\n')
                finallyContent = ''
                for index, value in enumerate(contenSplitList):
                    if index % 2 == 0:
                        finallyContent += '<p>' + value
                    else:
                        finallyContent += value + '</p>'
                    
                #for match in re.finditer(r'\\n',temptContent):
                    #s=match.start()
                   # e=match.end()
                   # print "Found %s at %d,%d" % (temptContent[s:e],s,e)
                self.content = temptContent.replace('\\n', '<br />')
                print self.content
                
class TelnetBBSContent():
    def __init__(self, urls):
        self.urls = urls
        self.finalInfo = []
        startTimeStamp =  datetime.now()
        endTimeStamp = datetime.now()+ timedelta(days=1)
        startTime = date(startTimeStamp.year, startTimeStamp.month, startTimeStamp.day).strftime("%Y-%m-%d %H:%M:%S")
        endTime = date(endTimeStamp.year, endTimeStamp.month, endTimeStamp.day).strftime("%Y-%m-%d %H:%M:%S")
        self.timeCondition = "saveTime between '" + startTime + "' and '" + endTime + "'"
        
    def getAllContent(self):
        print "2"
        sqlHelper = MySQLHelper('101.1.16.50','s559384db0','995y455y','s559384db0');
        print "3"
        if type(self.urls) == list:
            for urlItem in self.urls:
                sqlStr = "select infoId from tblJobInfo where bbsId = "+ str(urlItem["bbsId"]) + " and " + self.timeCondition
                print sqlStr
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
            
           
    def getContent(self, urlItem):
        print urlItem["url"]
        responseContent = requests.get(urlItem["url"]).content
        encoding = chardet.detect(responseContent)['encoding']
        if responseContent != 'utf-8':
            responseContent = responseContent.decode(encoding, 'replace').encode('utf-8')
        parser = TelnetBBSParser(responseContent)
        parser.getScriptContent(urlItem["flag"], "script")
        self.content = parser.content
        self.parserContent(urlItem)
    
    def parserContent(self, urlItem):
        contentList = self.content.split(";")
        flag = ["校招", "实习生", "Intern", "intern"]
        antiFlag = ["指导", "版规", "Re"]
        jobInfo = {}
        jobInfo["infoList"] = []
        isContiue = True
        yesterdayTime =  datetime.now() - timedelta(days=1)
        yesterday = date(yesterdayTime.year, yesterdayTime.month, yesterdayTime.day)
        for index, cont in enumerate(contentList):
            outer = re.compile("\((.+)\)")
            m = outer.search(cont)
            if m is not None:
                inner_str = m.group(1)
                innerList = inner_str.split(",")
                if index == 0:
                    jobInfo["bid"] = innerList[1]
                    jobInfo["lastPage"] = int(innerList[5]) - 1
                elif index != len(contentList)-2:
                    timeStamp = (int(innerList[4]))
                    tmpltime = datetime.fromtimestamp(timeStamp)
                    pubTime = tmpltime.strftime("%Y-%m-%d %H:%M:%S")
                    pubDate = date(tmpltime.year, tmpltime.month, tmpltime.day)
                    if str(pubDate) == str(yesterday):
                        isContiue = False
                        break
                    elif any(keyword in cont for keyword in flag) and any(keyword not in cont for keyword in antiFlag):
                        infoId = innerList[0]
                        if infoId not in self.existInfoIdList:
                            contentUrl = urlItem["contentUrl"] + "bid=" + jobInfo["bid"] + "&id=" + innerList[0]
                            self.existInfoIdList.append(infoId)
                            contentParser = TelnetContent({
                                               "url":contentUrl,
                                               "contentFlag":"attWriter",
                                               "parseFlag":"prints"
                                               })
                            infoDetail = {
                                  "infoId": infoId,
                                  "href": contentUrl,
                                  "saveTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  "bbsId": urlItem["bbsId"],
                                  "publishTime": pubTime,
                                  "title": "'"+ innerList[5].encode('UTF-8') + "'",
                                  "content": contentParser.content
                                  }
                            jobInfo["infoList"].append(infoDetail)
        self.finalInfo.extend(jobInfo["infoList"])
        if isContiue == True:
            urlItem["url"] = urlItem["url"] + "&page=" + str(jobInfo["lastPage"]);
            self.getContent(urlItem)
        
