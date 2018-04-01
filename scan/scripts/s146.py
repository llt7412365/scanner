# -*- coding: utf-8 -*- 
import os
import time
import subprocess
from subprocess import Popen,PIPE

def telnet(cmd, timeout=15):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            res = p.communicate()
            exitcode = p.poll() if p.poll() else 0
            return
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            out, exitcode, err = '', 128, 'timeout'
            return

def kill(host):
	output = os.popen('ps -ef | grep '+host)
	data = output.read()
	pid_list = []
	a= data.split('\n')
	for i in a:
		if 'grep' in i and '|' not in i:
			continue
		print i
		b= i.split(' ')
		while '' in b:
			b.remove('')
		if b:
			pid_list.append(b[1])
	for i in pid_list:
		cmd = 'kill -9 '+str(i)
		os.system(cmd)


def start(host,port,pro):
	try:
		content = ''
		up = {'winda':'huawei','admin':'admin'}
		for i in up:
			user = i
			password = up[i]
			cmd = "python /var/www/html/ngscanner/scan/scripts/send_telnet.py "+host+" "+user+" "+password+" >telnet_data.txt"
			telnet(cmd)
			data_file = open('telnet_data.txt')
			data = data_file.read( ).strip()
			kill(host)
			os.remove('/var/www/html/ngscanner/scan/scripts/telnet_data.txt')
			data_list = data.split('\n')
			if '<' and '>' in data_list[-1]:
				content = user+':'+password
		if ':' in content:
			return 1,'',content
		else:
			return 0,0,0
	except Exception, e:
		return 0,0,0

if __name__ == '__main__':
	print start('112.53.84.234','','')