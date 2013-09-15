# encoding: utf-8
from MySQLHelper import MySQLHelper
from TelnetBBSParser import TelnetBBSContent
from BYRBBSParser import BYRBBSParser
from datetime import * 

def insetToDB():
    jobInfo = []
    telnetBbsContent = TelnetBBSContent([{
                      "url": "http://www.newsmth.net/bbsdoc.php?board=Career_Campus",
                      "contentUrl": "http://www.newsmth.net/bbscon.php?",
                      "bbsId": 2,
                      "flag":"docWriter"
                      },{
                      "url": "http://www.lsxk.org/bbsdoc.php?board=Part_timeJob",
                      "contentUrl": "http://www.lsxk.org/bbscon.php?",
                      "bbsId": 6,
                      "flag":"docWriter"
                      }])
    telnetBbsContent.getAllContent()
    
    BYRbbsContent = BYRBBSParser({
                      "url": "http://bbs.byr.cn/board/JobInfo?p=",
                      "contentUrl": "http://bbs.byr.cn",
                      "bbsId":4,
                      "selector": {
                                   "parseAnchor":  ".title_9",
                                   "parserTimeStamp": ".title_10"
                                   }
                      })
    BYRbbsContent.getAllContent()
    print "-----------------------*******-------------------------------"
    print "BYR: " + str(BYRbbsContent.finalInfo)
    print "Telnet: " + str(telnetBbsContent.finalInfo)
    print "SaveTime: " +datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print "-----------------------*******-------------------------------"
    jobInfo.extend(telnetBbsContent.finalInfo)
    jobInfo.extend(BYRbbsContent.finalInfo)
    sqlHelper = MySQLHelper('101.1.16.50','s559384db0','995y455y','s559384db0'); 
    for value in jobInfo:
        print value
        sqlHelper.insert("tblJobInfo", value)
insetToDB()