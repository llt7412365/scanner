#coding:utf8
import os
import sys
import zlib
import time
import lytool
import lyLog
import string
import chardet
import logging
import urlparse
import traceback
from time import strftime
from netlib import http
from pymongo import MongoClient
from urllib import unquote_plus
from StringIO import StringIO
from libmproxy import flow
from libmproxy import encoding
from libmproxy import controller, proxy
from libmproxy.proxy.server import ProxyServer
from libmproxy.protocol.http import decoded, encoding
from BaseHTTPServer import BaseHTTPRequestHandler

SITE_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)),'..')
sys.path.append(SITE_ROOT)
sys.path.append("..")
from up.models import *
from lingyun.settings import IP_Local 

class HTTPRequest(BaseHTTPRequestHandler):
	def __init__(self,request_text):
		self.rfile = StringIO(request_text)
		self.raw_requestline = self.rfile.readline()
		self.error_code = self.error_message = None
		self.parse_request()

class StickyMaster(controller.Master):
	def __init__(self,server):
		controller.Master.__init__(self,server)

	def run(self):
		try:
			return controller.Master.run(self)
		except KeyboardInterrupt:
			self.shutdown()

	def db_conn(self):
		client = MongoClient(IP_Local,27017)
		db = client.db_lingyun
		return db


	def ana_host(self,host,port):
		all_host = []
		host_list = []
		df = []
		lis = self.db_conn().tbl_business.find({},{'sites':1})
		for h in lis:
			all_host+=(h['sites'])
		for i in all_host:
			if i not in host_list:
				host_list.append(i)
		for j in host_list:
			if ':' in j:
				site = j.split(':')
				if site[0] in host and site[-1] == str(port):
					df.append(1)
				else:
					df.append(0)
			else:
				if j in host:
					df.append(1)
				else:
					df.append(0)
		if 1 not in df:
			return 1
		else:
			return 0

				
	#过滤content(第3层筛选)
	def ana2(self,reqcontent):
		if reqcontent:
			content = '%s'*len(reqcontent) %tuple(reqcontent)
			if 'image/' in content or 'application/x-shockwave-flash' in content \
			or 'application/octet-stream' in content or 'application/ocsp-response' in content \
			or 'boundary=GJircTeP' in content:
				return 1
			else:
				return 0



#收集请求数据
	def handle_request(self,flow):
		host = flow.request.host
		method = flow.request.method
		scheme = flow.request.scheme
		port = flow.request.port
		path = flow.request.path
		httpversion = flow.request.httpversion
		headers = flow.request.headers
		content = flow.request.content
		url = flow.request.url
		if self.ana_host(host,port):
			pass
		else:
			self.db_save1(url,host,port)
		flow.reply()

	def handle_response(self,flow):
		url = flow.request.url
		method = flow.request.method
		content1 = flow.request.content
		resc = flow.response.headers.get('Content-type')
		reqc = flow.request.headers.get('Content-type')
		host = flow.request.host
		port = flow.request.port
		if lytool.filter_url(url) or self.ana2(reqc) or self.ana2(resc) or self.ana_host(host,port):
			pass
		else:
			host = flow.request.host
			port = flow.request.port
			url = unquote_plus(flow.request.url)
			path = flow.request.path
			scheme = flow.request.scheme
			method = flow.request.method
			httpversion = flow.request.httpversion
			headers1 = flow.request.headers
			headers2 = flow.response.headers
			content1 = flow.request.content
			content = flow.response.content
			gzipped = flow.response.headers.get_first("content-encoding")
			if gzipped:
				content2 = encoding.decode(gzipped, content)
			else:
				content2 = content			
			self.db_save(host,port,url,path,method,scheme,httpversion,headers1,content1,headers2,content2)
			
		flow.reply()

	def db_save(self,host,port,url,path,method,scheme,httpversion,headers1,content1,headers2,content2):

		tempdb = TblTempInfo()	
		tempdb.host = host
		tempdb.port = port
		tempdb.url =  url
		tempdb.path =  path
		tempdb.method =  method
		tempdb.scheme =  scheme
		tempdb.httpversion =  str(httpversion)
		tempdb.req_header =  str(headers1)
		tempdb.req_content =  content1
		tempdb.res_header = str(headers2)
		tempdb.res_content =  lytool.decode(content2)
		tempdb.add_time =  time.time()
		try:
			tempdb.save()
		except Exception,e:
			info = sys.exc_info()
			level = 4
			lylog = lyLog.lyLog('info_log',info,level)
			lylog.buildLog()

	def db_save1(self,url,site,port):
		tempurl = TblTempUrl()
		tempurl.url = url
		tempurl.site = site
		tempurl.port = port
		tempurl.add_time = time.time()
		try:
			tempurl.save()
		except Exception,e:
			info = sys.exc_info()
			level = 4
			lylog = lyLog.lyLog('info_log',info,level)
			lylog.buildLog()
			
def run_all():
	config = proxy.ProxyConfig(port=8080)
	server = ProxyServer(config)
	m = StickyMaster(server)
	m.run()

# if __name__ == '__main__':
# 	run_all()