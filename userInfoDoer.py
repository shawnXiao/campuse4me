# This Python file uses the following encoding: utf-8
import requests
from WechartToken import WechartToken
from urlparse import urlparse, parse_qsl
from datetime import * 
import time
from MySQLHelper import MySQLHelper


def getUserInfo():
    wecharInfo = WechartToken("85770253@qq.com", "44137b278ed88938e29626e010e8e159")
    wecharInfo.getUserFakeId()
    wecharInfo.getContact()
getUserInfo()