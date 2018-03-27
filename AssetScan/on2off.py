import os

def start(t_id,fun):
	command = 'sudo /usr/local/bin/python /var/www/html/ngscanner/scan/switch.py '+str(t_id)+' '+str(fun)
	output = os.popen(command)
	return output.read()
start(1,'stop')