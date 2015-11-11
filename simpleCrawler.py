#!/usr/bin/env python
# -*- coding = utf-8 -*-
import threading
import urllib
import re
import time

g_mutex = threading.Condition()	# use to access global variable
g_pages = []		# store the whole pages of download content
g_queueURL = []		# waited url 
g_existURL = []		# url that has downloaded
g_failedURL = []	# faild url
g_totalcount = 0	# total url number

class Crawler:
	def __init__(self, crawlername, url, threadnum):
		self.crawlername = crawlername
		self.url = url
		self.threadnum = threadnum
		self.threadpool = []
		self.logfile = file("log.txt",'a')

	def craw(self):
		global g_queueURL
		g_queueURL.append(url)    
		depth = 0
		print self.crawlername + " launching..."
		while(len(g_queueURL) != 0):
			depth += 1
			print 'searching depth ', depth , '...\n'
			self.logfile = open("log.txt", 'a')
			self.logfile.write("URL:" + g_queueURL[0] + "........")
			self.downloadAll()
			self.updateQueueURL()
			content = '\n>>>Depth ' + str(depth) + ':\n'
			self.logfile.write(content)
			i = 0
			while i < len(g_queueURL):
				content = str(g_totalcount+i) + '->' + g_queueURL[i] + '\n'
				self.logfile.write(content)
				i += 1
			self.logfile.close()

	def downloadAll(self):
		global g_queueURL
		global g_totalcount
		i = 0
		while i < len(g_queueURL):
			j = 0
			while j < self.threadnum and i+j < len(g_queueURL):
				g_totalcount += 1
				threadresult = self.download(g_queueURL[i+j], str(g_totalcount) + '.html', j)
				if threadresult != None:
					print 'Thread started:', i+j ,'--File number =', g_totalcount
				j += 1
			i += j
			for thread in self.threadpool:
				thread.join(30)
			threadpool = []
		g_queueURL = []

	def download(self, url, filename, tid):
		crawthread=CrawlerThread(url, filename, tid)
		self.threadpool.append(crawthread)
		crawthread.start()

	def updateQueueURL(self):
		global g_queueURL
		global g_existURL
		newUrlList = []
		for content in g_pages:
			newUrlList += self.getUrl(content)
		g_queueURL = list(set(newUrlList) - set(g_existURL))

	def getUrl(self,content):
		reg = r'"(http://.+?)"'
		regob = re.compile(reg, re.DOTALL)
		urllist = regob.findall(content)
		return urllist

class CrawlerThread(threading.Thread):
	def __init__(self, url, filename,tid):
		threading.Thread.__init__(self)
		self.url = url
		self.filename = filename
		self.tid = tid

	def run(self):
		global g_mutex
		global g_failedURL
		global g_queueURL
		try:
			page = urllib.urlopen(self.url)
			html = page.read()
			fout = open(self.filename,'w')
			fout.write(html)
			fout.close()
		except Exception,e:
			g_mutex.acquire()
			g_existURL.append(self.url)
			g_failedURL.append(self.url)
			g_mutex.release()
			print 'Failed downloading and saving', self.url
			print e
			return None
		g_mutex.acquire()
		g_pages.append(html)
		g_existURL.append(self.url)
		g_mutex.release()
		

if __name__ == '__main__':
	url= "http://" + raw_input("input url(no http):\n")
	threadnum = int(raw_input("set thread number:"))
	crawlername = "simple crawler"
	crawler = Crawler(crawlername,url,threadnum)
	crawler.craw()
