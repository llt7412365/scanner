#coding:utf-8


import ftplib


def connect(host,user,pwd):
	try:
		ftp = ftplib.FTP()                            
		ftp.connect(host,21,timeout=10)
		ftp.login(user,pwd)                             
		ftp.quit()
		return 1
	except:
		return 0

def start(host,port,pro):
	try:
		state_list = []
		user_list = ['dajie']
		pass_list = ['321456', 'test', '123456', 'password', 'root', 'admin','qaz123','111111']
		for i in user_list:
			for j in pass_list:
				state = connect(host,i,j)
				if state:
					return 1,'',i+':'+j
		return 0,0,0
	except:
		return 0,0,0