# This Python file uses the following encoding: utf-8
from bs4 import BeautifulSoup
import re
import urllib
import urllib2
import urllib
import urllib2
import chardet
import mechanize
import sys
import json

reload( sys )
sys.setdefaultencoding('utf-8')

Main_URL = "http://s.yingjiesheng.com/result.jsp?do=1&stype=0"
#see http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser
DEFAULT_PARSER = "html.parser"
# how long to try to open a URL before timing out
TIMEOUT=60.0
class JobHunterEngin():
    def __init__(self, keyWord, city, proxy=None, parser=DEFAULT_PARSER,):
        self.city = city
        self.keyWord = keyWord
        self.proxy = proxy
        self.parser = parser
        self.urlPart = "&keyword="+ keyWord + "&city=" + city
        self.search_url = Main_URL + self.urlPart
        self.searchResult = []

    def initBr(self):
        br = mechanize.Browser()
        #br.set_debug_http(True)
        #br.set_debug_responses(False)
        #br.set_debug_redirects(True)
        br.set_handle_robots(False)

        if self.proxy:
            br.set_proxies({"http":self.proxy})
        self.browser = br
    def fetch(self):
        # get the course name, and redirect to the course lecture page
        print self.search_url
        vidpage = self.browser.open(self.search_url,timeout=TIMEOUT)

        # extract the weekly classes
        soup = BeautifulSoup(vidpage,self.parser)

        # extract the weekly classes
        searchList = soup.select(".searchResult li")
        for searchItem in searchList:
            title = searchItem.select(".title")
            title_txt = title[0].a.text.strip()
            date = searchItem.select(".date")
            date_txt = date[0].text.strip()
            anchor = searchItem.select(".title a")
            content_url = anchor[0].get("href")
            self.searchResult.append({
              "title": title_txt.encode("utf-8"),
              "date": date_txt.encode("utf-8"),
              "content_url":content_url.encode("utf-8")
              })

            #contentPage = self.browser.open(content_url, timeout=TIMEOUT)
            #contentSoup = BeautifulSoup(contentPage, self.parser)
            #content_text = contentSoup.find("div", {'class':'jobIntro'})
            #if not content_text:
                #content_text = contentSoup.find("div", {'class':'job_list'})
                #if  content_text is not None:
                    #if not content_text('script'):
                        #[s.extract() for s in content_text('script')]
                    #if not content_text.find("div", {'class':'job_sq'}):
                        #[s.extract() for s in content_text.find("div", {'class':'job_sq'})]
                    #self.searchResult.append({
                                              #"title": title_txt.encode("utf-8"),
                                              #"date": date_txt.encode("utf-8"),
                                              #"content_url":content_url.encode("utf-8")
                                              #})
                    #print date_txt
                    #print title_txt
                    #print content_url
            #else :
                #invalid_tag = content_text('p')
                #if len(invalid_tag) >= 2:
                    #invalid_tag[-1].extract()
                    #invalid_tag[-2].extract()
                    #self.searchResult.append({
                                              #"title": title_txt.encode("utf-8"),
                                              #"date": date_txt.encode("utf-8"),
                                              #"content_url":content_url.encode("utf-8")
                                              #})
                    #print date_txt
                    #print title_txt
                    #print content_url
        result_obj = {"searchResutl":self.searchResult}
        print json.dumps(result_obj)
        return json.dumps(result_obj)



        #searchList = searchResult
def main():
    jobHunterTest = JobHunterEngin("hr", "0")
    jobHunterTest.initBr()
    print jobHunterTest.fetch()
if __name__ == '__main__':
    main()
