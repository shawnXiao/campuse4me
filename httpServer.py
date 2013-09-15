# This Python file uses the following encoding: utf-8
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading
import urlparse
import argparse
import re
import cgi
import searchEngin

class LocalData():
    records = {}
    def __init__(self, keyword, city):
        self.keyword = keyword
        self.city = city
    def fetch(self):
        jobHunterTest = searchEngin.JobHunterEngin(self.keyword, self.city)
        jobHunterTest.initBr()
        return jobHunterTest.fetch()
       

class HTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if None != re.search('/api/v1/addrecord/*', self.path):
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            length = int(self.headers.getheader('content-length'))
            data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            recordID = self.path.split('/')[-1]
            queryList =  urlparse.parse_qs(urlparse.urlparse(self.path).query)
            city = queryList["city"]
            keyword = queryList["keyword"]
            LocalData.records[recordID] = data
            print "record %s is added successfully" % recordID

            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

        return

    def do_GET(self):
        if None != re.search('/api/*', self.path):
            recordID = self.path.split('/')[-1]
            queryList =  urlparse.parse_qs(urlparse.urlparse(self.path).query)
            print queryList
            city = queryList["city"][0]
            keyword = queryList["keyword"][0]
            print queryList["keyword"][0]
            records = LocalData(keyword, city)
            searchResutl = records.fetch()
            if searchResutl:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(searchResutl)
            else:
                self.send_response(400, 'Bad Request: record does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
        else:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)

class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer(("116.255.163.99",3721), HTTPRequestHandler)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    def addRecord(self, recordID, jsonEncodedRecord):
        LocalData.records[recordID] = jsonEncodedRecord

    def stop(self):
        self.server.shutdown()
        self.waitForThread()

if __name__=='__main__':

    server = SimpleHttpServer("localhost",8080)
    print 'HTTP Server Running...........'
    server.start()
    server.waitForThread()
